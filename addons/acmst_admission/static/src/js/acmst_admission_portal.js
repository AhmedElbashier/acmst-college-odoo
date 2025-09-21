/* ACMST Admission Module - Portal JavaScript */

odoo.define('acmst_admission.portal', ['web.public.widget', 'web.ajax', 'web.core'], function (publicWidget, ajax, core) {
    'use strict';

    var _t = core._t;

    // Portal Application Form Widget
    var PortalApplicationForm = publicWidget.Widget.extend({
        selector: '.acmst-portal-application-form',
        events: {
            'submit form': '_onFormSubmit',
            'change input, select, textarea': '_onFieldChange',
            'click .acmst-btn': '_onButtonClick',
            'dragover .acmst-file-upload': '_onDragOver',
            'dragleave .acmst-file-upload': '_onDragLeave',
            'drop .acmst-file-upload': '_onDrop',
            'change input[type="file"]': '_onFileChange'
        },

        start: function () {
            this._super.apply(this, arguments);
            this._initializeForm();
            this._setupValidation();
            this._setupFileUpload();
            this._setupProgressBar();
            this._setupWizard();
            this._setupAutoSave();
        },

        _initializeForm: function () {
            var self = this;
            
            // Set default values
            this.$('input[name="nationality"]').val('Saudi');
            this.$('select[name="gender"]').val('male');
            
            // Set minimum date for birth date (18 years ago)
            var minDate = new Date();
            minDate.setFullYear(minDate.getFullYear() - 18);
            this.$('input[name="birth_date"]').attr('max', minDate.toISOString().split('T')[0]);
            
            // Set maximum date for birth date (100 years ago)
            var maxDate = new Date();
            maxDate.setFullYear(maxDate.getFullYear() - 100);
            this.$('input[name="birth_date"]').attr('min', maxDate.toISOString().split('T')[0]);
        },

        _setupValidation: function () {
            var self = this;
            
            // Real-time validation
            this.$('input[required], select[required], textarea[required]').on('blur', function() {
                self._validateField($(this));
            });
            
            // Enhanced National ID validation
            this.$('input[name="national_id"]').on('input', function() {
                var value = $(this).val().replace(/\D/g, ''); // Remove non-digits
                $(this).val(value); // Update field with cleaned value
                
                if (value.length > 0 && value.length < 10) {
                    self._showFieldError($(this), 'National ID must be exactly 10 digits');
                } else if (value.length === 10) {
                    if (!self._validateSaudiNationalID(value)) {
                        self._showFieldError($(this), 'Invalid National ID format');
                    } else {
                        self._clearFieldError($(this));
                    }
                } else {
                    self._clearFieldError($(this));
                }
            });
            
            // Enhanced Email validation
            this.$('input[name="email"]').on('blur', function() {
                var value = $(this).val().trim();
                if (value && !self._validateEmail(value)) {
                    self._showFieldError($(this), 'Please enter a valid email address');
                } else {
                    self._clearFieldError($(this));
                }
            });
            
            // Enhanced Phone validation
            this.$('input[name="phone"]').on('input', function() {
                var value = $(this).val();
                var cleaned = value.replace(/\D/g, '');
                
                if (cleaned.length > 0) {
                    // Format phone number
                    var formatted = self._formatPhoneNumber(cleaned);
                    $(this).val(formatted);
                }
                
                if (value && !self._validatePhone(value)) {
                    self._showFieldError($(this), 'Please enter a valid phone number');
                } else {
                    self._clearFieldError($(this));
                }
            });
            
            // Name validation
            this.$('input[name="applicant_name_english"], input[name="applicant_name_arabic"]').on('blur', function() {
                var value = $(this).val().trim();
                if (value && !self._validateName(value)) {
                    self._showFieldError($(this), 'Name must contain only letters and spaces');
                } else {
                    self._clearFieldError($(this));
                }
            });
            
            // Birth date validation
            this.$('input[name="birth_date"]').on('change', function() {
                var value = $(this).val();
                if (value && !self._validateBirthDate(value)) {
                    self._showFieldError($(this), 'You must be at least 16 years old to apply');
                } else {
                    self._clearFieldError($(this));
                }
            });
            
            // Address validation
            this.$('textarea[name="address"]').on('blur', function() {
                var value = $(this).val().trim();
                if (value && value.length < 10) {
                    self._showFieldError($(this), 'Please provide a more detailed address');
                } else {
                    self._clearFieldError($(this));
                }
            });
        },

        _setupFileUpload: function () {
            var self = this;
            var $fileUpload = this.$('.acmst-file-upload');
            var $fileInput = this.$('input[type="file"]');
            
            if ($fileUpload.length && $fileInput.length) {
                // Click to upload
                $fileUpload.on('click', function() {
                    $fileInput.click();
                });
                
                // File selection
                $fileInput.on('change', function() {
                    var files = this.files;
                    if (files.length > 0) {
                        self._handleFileSelection(files);
                    }
                });
                
                // Drag and drop functionality
                $fileUpload.on('dragover', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    $(this).addClass('dragover');
                });
                
                $fileUpload.on('dragleave', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    $(this).removeClass('dragover');
                });
                
                $fileUpload.on('drop', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    $(this).removeClass('dragover');
                    
                    var files = e.originalEvent.dataTransfer.files;
                    if (files.length > 0) {
                        self._handleFileSelection(files);
                    }
                });
            }
        },

        _setupProgressBar: function () {
            var self = this;
            var $progressBar = this.$('.acmst-progress-bar');
            
            if ($progressBar.length) {
                // Calculate progress based on filled fields
                this._updateProgress();
                
                // Update progress on field changes
                this.$('input, select, textarea').on('change', function() {
                    self._updateProgress();
                });
            }
        },

        _setupWizard: function () {
            var self = this;
            this.currentStep = 1;
            this.totalSteps = 4;
            
            // Setup step navigation
            this.$('#next-step').on('click', function() {
                self._nextStep();
            });
            
            this.$('#prev-step').on('click', function() {
                self._prevStep();
            });
            
            // Setup step click navigation
            this.$('.acmst-progress-steps .step').on('click', function() {
                var step = parseInt($(this).data('step'));
                if (step <= self.currentStep || self._isStepCompleted(step)) {
                    self._goToStep(step);
                }
            });
            
            this._updateWizardUI();
        },

        _setupAutoSave: function () {
            var self = this;
            var autoSaveInterval = 30000; // 30 seconds
            
            // Auto-save on field changes
            this.$('input, select, textarea').on('change', function() {
                clearTimeout(self.autoSaveTimeout);
                self.autoSaveTimeout = setTimeout(function() {
                    self._autoSave();
                }, 2000); // Save 2 seconds after last change
            });
        },

        _nextStep: function () {
            if (this._validateCurrentStep()) {
                if (this.currentStep < this.totalSteps) {
                    this.currentStep++;
                    this._goToStep(this.currentStep);
                }
            }
        },

        _prevStep: function () {
            if (this.currentStep > 1) {
                this.currentStep--;
                this._goToStep(this.currentStep);
            }
        },

        _goToStep: function (step) {
            var self = this;
            
            // Hide all steps
            this.$('.wizard-step').removeClass('active');
            
            // Show current step
            this.$('.wizard-step[data-step="' + step + '"]').addClass('active');
            
            // Update progress steps
            this.$('.acmst-progress-steps .step').each(function() {
                var stepNum = parseInt($(this).data('step'));
                $(this).removeClass('active completed');
                
                if (stepNum < step) {
                    $(this).addClass('completed');
                } else if (stepNum === step) {
                    $(this).addClass('active');
                }
            });
            
            // Update progress bar
            var progress = ((step - 1) / (this.totalSteps - 1)) * 100;
            this.$('.acmst-progress-bar').css('width', progress + '%');
            
            // Update navigation buttons
            this.$('#prev-step').prop('disabled', step === 1);
            this.$('#next-step').text(step === this.totalSteps ? 'Submit' : 'Next');
            
            // Update step progress text
            this.$('.acmst-section-progress .progress-text').text('Step ' + step + ' of ' + this.totalSteps);
            
            // Generate summary if on last step
            if (step === this.totalSteps) {
                this._generateApplicationSummary();
            }
        },

        _validateCurrentStep: function () {
            var self = this;
            var isValid = true;
            var $currentStep = this.$('.wizard-step.active');
            
            // Validate required fields in current step
            $currentStep.find('input[required], select[required], textarea[required]').each(function() {
                if (!self._validateField($(this))) {
                    isValid = false;
                }
            });
            
            return isValid;
        },

        _isStepCompleted: function (step) {
            var self = this;
            var $step = this.$('.wizard-step[data-step="' + step + '"]');
            var isCompleted = true;
            
            // Check if all required fields in step are filled
            $step.find('input[required], select[required], textarea[required]').each(function() {
                if (!$(this).val() || $(this).val().trim() === '') {
                    isCompleted = false;
                    return false;
                }
            });
            
            return isCompleted;
        },

        _updateWizardUI: function () {
            this._goToStep(this.currentStep);
        },

        _autoSave: function () {
            var self = this;
            var formData = this._getFormData();
            
            // Show save indicator
            this.$('.acmst-save-indicator').addClass('saving');
            
            ajax.jsonRpc('/admission/save_draft', 'call', formData)
                .then(function(result) {
                    if (result.success) {
                        self.$('.acmst-save-indicator').removeClass('saving').addClass('saved');
                        setTimeout(function() {
                            self.$('.acmst-save-indicator').removeClass('saved');
                        }, 2000);
                    }
                })
                .catch(function(error) {
                    console.error('Auto-save failed:', error);
                });
        },

        _generateApplicationSummary: function () {
            var self = this;
            var summary = '<div class="summary-content">';
            
            // Personal Information
            summary += '<div class="summary-section">';
            summary += '<h5>Personal Information</h5>';
            summary += '<div class="summary-item"><strong>Name:</strong> ' + this.$('input[name="applicant_name_english"]').val() + '</div>';
            summary += '<div class="summary-item"><strong>Phone:</strong> ' + this.$('input[name="phone"]').val() + '</div>';
            summary += '<div class="summary-item"><strong>Email:</strong> ' + this.$('input[name="email"]').val() + '</div>';
            summary += '<div class="summary-item"><strong>National ID:</strong> ' + this.$('input[name="national_id"]').val() + '</div>';
            summary += '</div>';
            
            // Admission Details
            summary += '<div class="summary-section">';
            summary += '<h5>Admission Details</h5>';
            summary += '<div class="summary-item"><strong>Program:</strong> ' + this.$('select[name="program_id"] option:selected').text() + '</div>';
            summary += '<div class="summary-item"><strong>Batch:</strong> ' + this.$('select[name="batch_id"] option:selected').text() + '</div>';
            summary += '<div class="summary-item"><strong>Admission Type:</strong> ' + this.$('select[name="admission_type"] option:selected').text() + '</div>';
            summary += '</div>';
            
            // Documents
            summary += '<div class="summary-section">';
            summary += '<h5>Documents</h5>';
            var fileCount = this.$('input[type="file"]')[0].files.length;
            summary += '<div class="summary-item"><strong>Files:</strong> ' + fileCount + ' file(s) uploaded</div>';
            summary += '</div>';
            
            summary += '</div>';
            
            this.$('#application-summary').html(summary);
        },

        _onFormSubmit: function (event) {
            event.preventDefault();
            var self = this;
            
            // If we're on the last step, submit the form
            if (this.currentStep === this.totalSteps) {
                if (this._validateForm()) {
                    this._submitForm();
                }
            } else {
                // Otherwise, go to next step
                this._nextStep();
            }
        },

        _onFieldChange: function (event) {
            var $field = $(event.currentTarget);
            this._validateField($field);
            this._updateProgress();
        },

        _onButtonClick: function (event) {
            var $button = $(event.currentTarget);
            var action = $button.data('action');
            
            if (action === 'save-draft') {
                event.preventDefault();
                this._saveDraft();
            } else if (action === 'submit') {
                event.preventDefault();
                this._submitForm();
            }
        },

        _onDragOver: function (event) {
            event.preventDefault();
            $(event.currentTarget).addClass('dragover');
        },

        _onDragLeave: function (event) {
            $(event.currentTarget).removeClass('dragover');
        },

        _onDrop: function (event) {
            event.preventDefault();
            $(event.currentTarget).removeClass('dragover');
            
            var files = event.originalEvent.dataTransfer.files;
            if (files.length > 0) {
                this._handleFileUpload(files[0]);
            }
        },

        _onFileChange: function (event) {
            var files = event.target.files;
            if (files.length > 0) {
                this._handleFileUpload(files[0]);
            }
        },

        _validateForm: function () {
            var isValid = true;
            var self = this;
            
            this.$('input[required], select[required], textarea[required]').each(function() {
                if (!self._validateField($(this))) {
                    isValid = false;
                }
            });
            
            return isValid;
        },

        _validateField: function ($field) {
            var value = $field.val();
            var isRequired = $field.prop('required');
            var isValid = true;
            
            if (isRequired && (!value || value.trim() === '')) {
                this._showFieldError($field, 'This field is required');
                isValid = false;
            } else {
                this._clearFieldError($field);
            }
            
            return isValid;
        },

        _showFieldError: function ($field, message) {
            this._clearFieldError($field);
            $field.addClass('is-invalid');
            
            var $error = $('<div class="invalid-feedback">' + message + '</div>');
            $field.after($error);
        },

        _clearFieldError: function ($field) {
            $field.removeClass('is-invalid').addClass('is-valid');
            $field.siblings('.invalid-feedback').remove();
        },

        // Enhanced validation methods
        _validateSaudiNationalID: function (id) {
            if (id.length !== 10) return false;
            
            // Check if first digit is 1 or 2
            if (id[0] !== '1' && id[0] !== '2') return false;
            
            // Validate using Saudi National ID algorithm
            var sum = 0;
            for (var i = 0; i < 9; i++) {
                var digit = parseInt(id[i]);
                if (i % 2 === 0) {
                    digit *= 2;
                    if (digit > 9) digit = Math.floor(digit / 10) + (digit % 10);
                }
                sum += digit;
            }
            
            var checkDigit = (10 - (sum % 10)) % 10;
            return checkDigit === parseInt(id[9]);
        },

        _validateEmail: function (email) {
            var emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
            return emailRegex.test(email);
        },

        _validatePhone: function (phone) {
            // Remove all non-digit characters
            var cleaned = phone.replace(/\D/g, '');
            
            // Check if it's a valid Saudi phone number (9 digits starting with 5)
            if (cleaned.length === 9 && cleaned[0] === '5') {
                return true;
            }
            
            // Check if it's a valid international format
            if (cleaned.length >= 10 && cleaned.length <= 15) {
                return true;
            }
            
            return false;
        },

        _formatPhoneNumber: function (phone) {
            var cleaned = phone.replace(/\D/g, '');
            
            if (cleaned.length === 9 && cleaned[0] === '5') {
                // Saudi format: 5XX XXX XXX
                return cleaned.replace(/(\d{3})(\d{3})(\d{3})/, '$1 $2 $3');
            } else if (cleaned.length > 9) {
                // International format: +XXX XXX XXX XXXX
                if (cleaned.startsWith('966')) {
                    return '+966 ' + cleaned.substring(3).replace(/(\d{3})(\d{3})(\d{3})/, '$1 $2 $3');
                } else {
                    return '+' + cleaned;
                }
            }
            
            return phone;
        },

        _validateName: function (name) {
            // Allow letters, spaces, hyphens, and apostrophes
            var nameRegex = /^[a-zA-Z\u0600-\u06FF\s\-']+$/;
            return nameRegex.test(name) && name.length >= 2;
        },

        _validateBirthDate: function (dateString) {
            var birthDate = new Date(dateString);
            var today = new Date();
            var age = today.getFullYear() - birthDate.getFullYear();
            var monthDiff = today.getMonth() - birthDate.getMonth();
            
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            
            return age >= 16 && age <= 100;
        },

        _updateProgress: function () {
            var $progressBar = this.$('.acmst-progress-bar');
            if (!$progressBar.length) return;
            
            var totalFields = this.$('input[required], select[required], textarea[required]').length;
            var filledFields = this.$('input[required], select[required], textarea[required]').filter(function() {
                return $(this).val() && $(this).val().trim() !== '';
            }).length;
            
            var progress = Math.round((filledFields / totalFields) * 100);
            $progressBar.css('width', progress + '%');
            $progressBar.attr('aria-valuenow', progress);
        },

        _updateFileUploadDisplay: function (file) {
            var $fileUpload = this.$('.acmst-file-upload');
            var $icon = $fileUpload.find('.acmst-file-upload-icon');
            var $text = $fileUpload.find('.acmst-file-upload-text');
            var $hint = $fileUpload.find('.acmst-file-upload-hint');
            
            $icon.removeClass('fa-cloud-upload-alt').addClass('fa-check-circle');
            $icon.css('color', '#28a745');
            $text.text(file.name);
            $hint.text('Click to change file');
        },

        _handleFileSelection: function (files) {
            var self = this;
            var validFiles = [];
            var errors = [];
            
            // Process each file
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                var validation = self._validateFile(file);
                
                if (validation.valid) {
                    validFiles.push(file);
                } else {
                    errors.push(file.name + ': ' + validation.error);
                }
            }
            
            // Show errors if any
            if (errors.length > 0) {
                this._showAlert('File validation errors:<br>' + errors.join('<br>'), 'danger');
            }
            
            // Add valid files to the list
            if (validFiles.length > 0) {
                this._addFilesToList(validFiles);
                this._updateFileUploadDisplay();
            }
        },

        _validateFile: function (file) {
            var allowedTypes = [
                'application/pdf',
                'image/jpeg',
                'image/jpg', 
                'image/png',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ];
            var maxSize = 10 * 1024 * 1024; // 10MB
            
            // Check file type
            if (!allowedTypes.includes(file.type)) {
                return {
                    valid: false,
                    error: 'Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG'
                };
            }
            
            // Check file size
            if (file.size > maxSize) {
                return {
                    valid: false,
                    error: 'File size exceeds 10MB limit'
                };
            }
            
            // Check file name length
            if (file.name.length > 255) {
                return {
                    valid: false,
                    error: 'File name too long (max 255 characters)'
                };
            }
            
            return { valid: true };
        },

        _addFilesToList: function (files) {
            var self = this;
            var $fileList = this.$('#file-list');
            
            if (!$fileList.length) {
                $fileList = $('<div class="acmst-file-list" id="file-list"></div>');
                this.$('.acmst-file-upload').after($fileList);
            }
            
            files.forEach(function(file) {
                var fileId = 'file_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                var fileItem = self._createFileItem(file, fileId);
                $fileList.append(fileItem);
            });
        },

        _createFileItem: function (file, fileId) {
            var self = this;
            var fileSize = self._formatFileSize(file.size);
            var fileIcon = self._getFileIcon(file.type);
            
            var $fileItem = $('<div class="file-item" data-file-id="' + fileId + '">' +
                '<div class="file-info">' +
                    '<div class="file-icon">' +
                        '<i class="fa fa-' + fileIcon + '"></i>' +
                    '</div>' +
                    '<div class="file-details">' +
                        '<div class="file-name">' + file.name + '</div>' +
                        '<div class="file-size">' + fileSize + '</div>' +
                    '</div>' +
                '</div>' +
                '<div class="file-actions">' +
                    '<button class="btn-preview" data-file-id="' + fileId + '">' +
                        '<i class="fa fa-eye"></i>' +
                    '</button>' +
                    '<button class="btn-remove" data-file-id="' + fileId + '">' +
                        '<i class="fa fa-times"></i>' +
                    '</button>' +
                '</div>' +
            '</div>');
            
            // Add event handlers
            $fileItem.find('.btn-remove').on('click', function() {
                self._removeFile(fileId);
            });
            
            $fileItem.find('.btn-preview').on('click', function() {
                self._previewFile(file);
            });
            
            return $fileItem;
        },

        _formatFileSize: function (bytes) {
            if (bytes === 0) return '0 Bytes';
            
            var k = 1024;
            var sizes = ['Bytes', 'KB', 'MB', 'GB'];
            var i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        _getFileIcon: function (fileType) {
            if (fileType.includes('pdf')) return 'file-pdf';
            if (fileType.includes('word') || fileType.includes('document')) return 'file-word';
            if (fileType.includes('image')) return 'file-image';
            return 'file';
        },

        _removeFile: function (fileId) {
            $('.file-item[data-file-id="' + fileId + '"]').remove();
            this._updateFileUploadDisplay();
        },

        _previewFile: function (file) {
            if (file.type.includes('image')) {
                this._previewImage(file);
            } else if (file.type.includes('pdf')) {
                this._previewPDF(file);
            } else {
                this._showAlert('Preview not available for this file type', 'info');
            }
        },

        _previewImage: function (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                var modal = $('<div class="file-preview-modal">' +
                    '<div class="modal-content">' +
                        '<div class="modal-header">' +
                            '<h5>Image Preview</h5>' +
                            '<button class="btn-close-modal">&times;</button>' +
                        '</div>' +
                        '<div class="modal-body">' +
                            '<img src="' + e.target.result + '" style="max-width: 100%; max-height: 500px;">' +
                        '</div>' +
                    '</div>' +
                '</div>');
                
                $('body').append(modal);
                
                modal.find('.btn-close-modal').on('click', function() {
                    modal.remove();
                });
                
                modal.on('click', function(e) {
                    if (e.target === modal[0]) {
                        modal.remove();
                    }
                });
            };
            reader.readAsDataURL(file);
        },

        _previewPDF: function (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                var modal = $('<div class="file-preview-modal">' +
                    '<div class="modal-content">' +
                        '<div class="modal-header">' +
                            '<h5>PDF Preview</h5>' +
                            '<button class="btn-close-modal">&times;</button>' +
                        '</div>' +
                        '<div class="modal-body">' +
                            '<iframe src="' + e.target.result + '" width="100%" height="500px"></iframe>' +
                        '</div>' +
                    '</div>' +
                '</div>');
                
                $('body').append(modal);
                
                modal.find('.btn-close-modal').on('click', function() {
                    modal.remove();
                });
                
                modal.on('click', function(e) {
                    if (e.target === modal[0]) {
                        modal.remove();
                    }
                });
            };
            reader.readAsDataURL(file);
        },

        _updateFileUploadDisplay: function () {
            var $fileUpload = this.$('.acmst-file-upload');
            var $icon = $fileUpload.find('.acmst-file-upload-icon');
            var $text = $fileUpload.find('.acmst-file-upload-text');
            var $hint = $fileUpload.find('.acmst-file-upload-hint');
            var fileCount = this.$('.file-item').length;
            
            if (fileCount > 0) {
                $icon.removeClass('fa-cloud-upload-alt').addClass('fa-check-circle');
                $icon.css('color', '#28a745');
                $text.text(fileCount + ' file(s) uploaded');
                $hint.text('Click to add more files or drag and drop');
            } else {
                $icon.removeClass('fa-check-circle').addClass('fa-cloud-upload-alt');
                $icon.css('color', '#6c757d');
                $text.text('Click to upload documents');
                $hint.html('<strong>Supported formats:</strong> PDF, DOC, DOCX, JPG, PNG<br/>' +
                          '<strong>Maximum size:</strong> 10MB per file<br/>' +
                          '<strong>Tip:</strong> Upload certificates, transcripts, and other supporting documents');
            }
        },

        _handleFileUpload: function (file) {
            // This method is kept for backward compatibility
            this._handleFileSelection([file]);
        },

        _saveDraft: function () {
            var self = this;
            var formData = this._getFormData();
            
            this._showLoading('Saving draft...');
            
            ajax.jsonRpc('/admission/save_draft', 'call', formData)
                .then(function(result) {
                    self._hideLoading();
                    if (result.success) {
                        self._showAlert('Draft saved successfully', 'success');
                    } else {
                        self._showAlert('Error saving draft: ' + result.error, 'danger');
                    }
                })
                .catch(function(error) {
                    self._hideLoading();
                    self._showAlert('Error saving draft', 'danger');
                });
        },

        _submitForm: function () {
            var self = this;
            var formData = this._getFormData();
            
            this._showLoading('Submitting application...');
            
            ajax.jsonRpc('/admission/submit', 'call', formData)
                .then(function(result) {
                    self._hideLoading();
                    if (result.success) {
                        self._showAlert('Application submitted successfully!', 'success');
                        setTimeout(function() {
                            window.location.href = '/admission/status/' + result.application_id;
                        }, 2000);
                    } else {
                        self._showAlert('Error submitting application: ' + result.error, 'danger');
                    }
                })
                .catch(function(error) {
                    self._hideLoading();
                    self._showAlert('Error submitting application', 'danger');
                });
        },

        _getFormData: function () {
            var formData = {};
            var self = this;
            
            this.$('input, select, textarea').each(function() {
                var $field = $(this);
                var name = $field.attr('name');
                var type = $field.attr('type');
                
                if (name) {
                    if (type === 'file') {
                        // Handle file upload
                        var files = this.files;
                        if (files.length > 0) {
                            formData[name] = files[0];
                        }
                    } else if (type === 'checkbox') {
                        formData[name] = $field.is(':checked');
                    } else {
                        formData[name] = $field.val();
                    }
                }
            });
            
            return formData;
        },

        _showLoading: function (message) {
            var $loading = $('<div class="acmst-loading">' +
                '<div class="acmst-spinner"></div>' +
                '<span>' + message + '</span>' +
                '</div>');
            
            this.$('.acmst-card').append($loading);
        },

        _hideLoading: function () {
            this.$('.acmst-loading').remove();
        },

        _showAlert: function (message, type) {
            var $alert = $('<div class="acmst-alert acmst-alert-' + type + '">' + message + '</div>');
            
            this.$('.acmst-card').prepend($alert);
            
            setTimeout(function() {
                $alert.fadeOut(function() {
                    $(this).remove();
                });
            }, 5000);
        }
    });

    // Portal Application Status Widget
    var PortalApplicationStatus = publicWidget.Widget.extend({
        selector: '.acmst-portal-application-status',
        events: {
            'click .acmst-btn': '_onButtonClick'
        },

        start: function () {
            this._super.apply(this, arguments);
            this._loadApplicationStatus();
        },

        _loadApplicationStatus: function () {
            var self = this;
            var applicationId = this.$el.data('application-id');
            
            if (applicationId) {
                ajax.jsonRpc('/admission/status/' + applicationId, 'call')
                    .then(function(result) {
                        self._updateStatusDisplay(result);
                    })
                    .catch(function(error) {
                        self._showError('Error loading application status');
                    });
            }
        },

        _updateStatusDisplay: function (data) {
            var $status = this.$('.acmst-status');
            var $progressBar = this.$('.acmst-progress-bar');
            var $details = this.$('.acmst-status-details');
            
            if ($status.length) {
                $status.removeClass().addClass('acmst-status acmst-status-' + data.state);
                $status.text(data.state_display);
            }
            
            if ($progressBar.length) {
                $progressBar.css('width', data.progress + '%');
            }
            
            if ($details.length) {
                $details.html(this._formatStatusDetails(data));
            }
        },

        _formatStatusDetails: function (data) {
            var html = '<div class="row">';
            
            html += '<div class="col-md-6">';
            html += '<h5>Application Information</h5>';
            html += '<p><strong>Application Number:</strong> ' + data.name + '</p>';
            html += '<p><strong>Applicant:</strong> ' + data.applicant_name + '</p>';
            html += '<p><strong>Program:</strong> ' + data.program_name + '</p>';
            html += '<p><strong>Submission Date:</strong> ' + data.submission_date + '</p>';
            html += '</div>';
            
            html += '<div class="col-md-6">';
            html += '<h5>Current Status</h5>';
            html += '<p><strong>State:</strong> ' + data.state_display + '</p>';
            html += '<p><strong>Progress:</strong> ' + data.progress + '%</p>';
            if (data.admission_file_id) {
                html += '<p><strong>Admission File:</strong> ' + data.file_number + '</p>';
            }
            html += '</div>';
            
            html += '</div>';
            
            return html;
        },

        _onButtonClick: function (event) {
            var $button = $(event.currentTarget);
            var action = $button.data('action');
            
            if (action === 'refresh') {
                event.preventDefault();
                this._loadApplicationStatus();
            }
        },

        _showError: function (message) {
            var $error = $('<div class="acmst-alert acmst-alert-danger">' + message + '</div>');
            this.$el.prepend($error);
        }
    });

    // Portal Health Check Widget
    var PortalHealthCheck = publicWidget.Widget.extend({
        selector: '.acmst-portal-health-check',
        events: {
            'submit form': '_onFormSubmit',
            'change input, select, textarea': '_onFieldChange',
            'click .acmst-btn': '_onButtonClick'
        },

        start: function () {
            this._super.apply(this, arguments);
            this._setupValidation();
            this._setupConditionalFields();
        },

        _setupValidation: function () {
            var self = this;
            
            // BMI calculation
            this.$('input[name="height"], input[name="weight"]').on('input', function() {
                self._calculateBMI();
            });
            
            // Conditional field visibility
            this.$('input[type="checkbox"]').on('change', function() {
                self._toggleConditionalFields();
            });
        },

        _setupConditionalFields: function () {
            this._toggleConditionalFields();
        },

        _toggleConditionalFields: function () {
            var self = this;
            
            this.$('input[type="checkbox"]').each(function() {
                var $checkbox = $(this);
                var $conditionalField = self.$('textarea[name="' + $checkbox.attr('name').replace('has_', '') + '_details"]');
                
                if ($checkbox.is(':checked')) {
                    $conditionalField.closest('.form-group').show();
                    $conditionalField.prop('required', true);
                } else {
                    $conditionalField.closest('.form-group').hide();
                    $conditionalField.prop('required', false).val('');
                }
            });
        },

        _calculateBMI: function () {
            var height = parseFloat(this.$('input[name="height"]').val());
            var weight = parseFloat(this.$('input[name="weight"]').val());
            
            if (height && weight && height > 0) {
                var heightM = height / 100;
                var bmi = weight / (heightM * heightM);
                this.$('input[name="bmi"]').val(bmi.toFixed(2));
            }
        },

        _onFormSubmit: function (event) {
            event.preventDefault();
            
            if (this._validateForm()) {
                this._submitHealthCheck();
            }
        },

        _onFieldChange: function (event) {
            var $field = $(event.currentTarget);
            this._validateField($field);
        },

        _onButtonClick: function (event) {
            var $button = $(event.currentTarget);
            var action = $button.data('action');
            
            if (action === 'save') {
                event.preventDefault();
                this._saveHealthCheck();
            } else if (action === 'submit') {
                event.preventDefault();
                this._submitHealthCheck();
            }
        },

        _validateForm: function () {
            var isValid = true;
            var self = this;
            
            this.$('input[required], select[required], textarea[required]').each(function() {
                if (!self._validateField($(this))) {
                    isValid = false;
                }
            });
            
            return isValid;
        },

        _validateField: function ($field) {
            var value = $field.val();
            var isRequired = $field.prop('required');
            var isValid = true;
            
            if (isRequired && (!value || value.trim() === '')) {
                this._showFieldError($field, 'This field is required');
                isValid = false;
            } else {
                this._clearFieldError($field);
            }
            
            return isValid;
        },

        _showFieldError: function ($field, message) {
            this._clearFieldError($field);
            $field.addClass('is-invalid');
            
            var $error = $('<div class="invalid-feedback">' + message + '</div>');
            $field.after($error);
        },

        _clearFieldError: function ($field) {
            $field.removeClass('is-invalid').addClass('is-valid');
            $field.siblings('.invalid-feedback').remove();
        },

        _saveHealthCheck: function () {
            // Implementation for saving health check
            console.log('Saving health check...');
        },

        _submitHealthCheck: function () {
            // Implementation for submitting health check
            console.log('Submitting health check...');
        }
    });

    // Notification System Widget
    var NotificationSystem = publicWidget.Widget.extend({
        selector: 'body',
        events: {
            'click .btn-close': '_onCloseNotification'
        },

        start: function () {
            this._super.apply(this, arguments);
            this._initializeNotificationSystem();
        },

        _initializeNotificationSystem: function () {
            // Create notification container if it doesn't exist
            if (!$('#notification-container').length) {
                $('body').append('<div class="acmst-notification-container" id="notification-container"></div>');
            }
            
            // Load existing notifications
            this._loadNotifications();
            
            // Set up auto-refresh for notifications
            setInterval(this._loadNotifications.bind(this), 30000); // Check every 30 seconds
        },

        _loadNotifications: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/notifications', 'call')
                .then(function(result) {
                    if (result.success) {
                        self._displayNotifications(result.notifications);
                    }
                })
                .catch(function(error) {
                    console.error('Error loading notifications:', error);
                });
        },

        _displayNotifications: function (notifications) {
            var self = this;
            var $container = $('#notification-container');
            
            // Clear existing notifications
            $container.empty();
            
            // Display new notifications
            notifications.forEach(function(notification) {
                self._showNotification(notification);
            });
        },

        _showNotification: function (notification) {
            var self = this;
            var $container = $('#notification-container');
            
            var $notification = $('<div class="acmst-notification acmst-notification-' + notification.type + '">' +
                '<div class="notification-icon">' +
                    '<i class="fa fa-' + notification.icon + '"></i>' +
                '</div>' +
                '<div class="notification-content">' +
                    '<h6>' + notification.title + '</h6>' +
                    '<p>' + notification.message + '</p>' +
                    '<small class="text-muted">' + notification.timestamp + '</small>' +
                '</div>' +
                '<div class="notification-actions">' +
                    '<button class="btn-close" data-notification-id="' + notification.id + '">' +
                        '<i class="fa fa-times"></i>' +
                    '</button>' +
                '</div>' +
            '</div>');
            
            $container.append($notification);
            
            // Auto-hide after 5 seconds
            setTimeout(function() {
                self._hideNotification($notification);
            }, 5000);
        },

        _hideNotification: function ($notification) {
            $notification.addClass('hide');
            setTimeout(function() {
                $notification.remove();
            }, 300);
        },

        _onCloseNotification: function (event) {
            var $button = $(event.currentTarget);
            var notificationId = $button.data('notification-id');
            var $notification = $button.closest('.acmst-notification');
            
            // Mark as read on server
            ajax.jsonRpc('/admission/notifications/mark_read', 'call', {
                notification_id: notificationId
            }).catch(function(error) {
                console.error('Error marking notification as read:', error);
            });
            
            // Hide notification
            this._hideNotification($notification);
        },

        // Public method to show notification
        showNotification: function (type, title, message, icon) {
            var notification = {
                id: Date.now(),
                type: type || 'info',
                title: title || 'Notification',
                message: message || '',
                icon: icon || 'info-circle',
                timestamp: new Date().toLocaleTimeString()
            };
            
            this._showNotification(notification);
        }
    });

    // Initialize widgets
    publicWidget.registry.acmstPortalApplicationForm = PortalApplicationForm;
    publicWidget.registry.acmstPortalApplicationStatus = PortalApplicationStatus;
    publicWidget.registry.acmstPortalHealthCheck = PortalHealthCheck;
    publicWidget.registry.acmstNotificationSystem = NotificationSystem;

    return {
        PortalApplicationForm: PortalApplicationForm,
        PortalApplicationStatus: PortalApplicationStatus,
        PortalHealthCheck: PortalHealthCheck,
        NotificationSystem: NotificationSystem
    };
});
