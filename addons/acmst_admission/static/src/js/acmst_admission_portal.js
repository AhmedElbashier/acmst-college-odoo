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
            
            // Real-time character counters
            this.$('textarea[name="address"]').on('input', function() {
                var value = $(this).val();
                var maxLength = $(this).attr('maxlength') || 500;
                var remaining = maxLength - value.length;
                
                var $counter = $(this).siblings('.character-counter');
                if (!$counter.length) {
                    $counter = $('<div class="character-counter text-muted small"></div>');
                    $(this).after($counter);
                }
                
                $counter.text(remaining + ' characters remaining');
                
                if (remaining < 50) {
                    $counter.removeClass('text-muted').addClass('text-warning');
                } else if (remaining < 0) {
                    $counter.removeClass('text-warning').addClass('text-danger');
                } else {
                    $counter.removeClass('text-warning text-danger').addClass('text-muted');
                }
            });
            
            // Real-time field completion indicators
            this.$('input[required], select[required], textarea[required]').on('input change', function() {
                self._updateFieldCompletion($(this));
            });
            
            // Form field focus effects
            this.$('input, select, textarea').on('focus', function() {
                $(this).closest('.form-group, .mb-3').addClass('focused');
            }).on('blur', function() {
                $(this).closest('.form-group, .mb-3').removeClass('focused');
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

        _updateFieldCompletion: function ($field) {
            var value = $field.val().trim();
            var isRequired = $field.prop('required');
            var $fieldGroup = $field.closest('.form-group, .mb-3');
            
            if (isRequired) {
                if (value !== '') {
                    $fieldGroup.addClass('field-completed');
                    $fieldGroup.removeClass('field-empty');
                } else {
                    $fieldGroup.removeClass('field-completed');
                    $fieldGroup.addClass('field-empty');
                }
            }
            
            // Update overall progress
            this._updateProgress();
            
            // Show smart notifications
            this._showSmartNotifications();
        },

        _showSmartNotifications: function () {
            var totalFields = this.$('input[required], select[required], textarea[required]').length;
            var filledFields = this.$('input[required], select[required], textarea[required]').filter(function() {
                return $(this).val() && $(this).val().trim() !== '';
            }).length;
            
            var percentage = Math.round((filledFields / totalFields) * 100);
            
            // Show progress notifications at key milestones
            if (percentage === 25 && filledFields === 1) {
                this._getNotificationSystem().showFormTip('Great start! Make sure to fill in your personal information completely.');
            } else if (percentage === 50) {
                this._getNotificationSystem().showFormTip('Halfway there! Don\'t forget to select your preferred program and batch.');
            } else if (percentage === 75) {
                this._getNotificationSystem().showFormTip('Almost done! Upload your supporting documents to complete the application.');
            } else if (percentage === 100) {
                this._getNotificationSystem().showFormProgress(filledFields, totalFields);
            }
        },

        _getNotificationSystem: function () {
            return publicWidget.registry.acmstNotificationSystem.prototype;
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
            this._setupRealTimeUpdates();
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
        },

        _setupRealTimeUpdates: function () {
            var self = this;
            
            // Set up periodic status updates
            this.statusUpdateInterval = setInterval(function() {
                self._checkStatusUpdates();
            }, 30000); // Check every 30 seconds
        },

        _checkStatusUpdates: function () {
            var self = this;
            var applicationId = this.$el.data('application-id');
            
            if (!applicationId) return;
            
            ajax.jsonRpc('/admission/status/check', 'call', {
                application_id: applicationId
            }).then(function(result) {
                if (result.success) {
                    self._updateStatusData(result.data);
                }
            }).catch(function(error) {
                console.error('Error checking status updates:', error);
            });
        },

        _updateStatusData: function (data) {
            // Update progress percentage
            if (data.progress_percentage !== undefined) {
                this.$('.progress-percentage').text(data.progress_percentage + '%');
                this.$('.progress-fill').css('width', data.progress_percentage + '%');
            }
            
            // Update status badge
            if (data.state) {
                this.$('.acmst-status').removeClass().addClass('acmst-status acmst-status-' + data.state).text(data.state);
            }
            
            // Add status update to live updates
            if (data.status_update) {
                this._addStatusUpdate(data.status_update);
            }
        },

        _addStatusUpdate: function (update) {
            var $updatesContainer = this.$('#status-updates');
            if (!$updatesContainer.length) return;
            
            var $updateItem = $('<div class="status-update-item">' +
                '<div class="update-icon">' +
                    '<i class="fa fa-' + (update.icon || 'info-circle') + '"></i>' +
                '</div>' +
                '<div class="update-content">' +
                    '<div class="update-title">' + update.title + '</div>' +
                    '<div class="update-message">' + update.message + '</div>' +
                    '<div class="update-time">' + update.timestamp + '</div>' +
                '</div>' +
            '</div>');
            
            $updatesContainer.prepend($updateItem);
            
            // Remove old updates if too many
            var $allUpdates = $updatesContainer.find('.status-update-item');
            if ($allUpdates.length > 10) {
                $allUpdates.slice(10).remove();
            }
            
            // Show notification if it's important
            if (update.important) {
                this._getNotificationSystem().showNotification(
                    update.type || 'info',
                    update.title,
                    update.message,
                    update.icon || 'info-circle'
                );
            }
        },

        _getNotificationSystem: function () {
            return publicWidget.registry.acmstNotificationSystem.prototype;
        },

        destroy: function () {
            // Clean up intervals
            if (this.statusUpdateInterval) {
                clearInterval(this.statusUpdateInterval);
            }
            this._super.apply(this, arguments);
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
        },

        // Form completion notifications
        showFormTip: function (message) {
            this.showNotification('info', 'Form Tip', message, 'lightbulb');
        },

        showFormProgress: function (completed, total) {
            var percentage = Math.round((completed / total) * 100);
            var message = `You've completed ${completed} of ${total} required fields (${percentage}%)`;
            
            if (percentage === 100) {
                this.showNotification('success', 'Form Complete!', 'All required fields have been filled. You can now proceed to the next step.', 'check-circle');
            } else if (percentage >= 75) {
                this.showNotification('info', 'Almost There!', message + '. Just a few more fields to go!', 'clock');
            } else if (percentage >= 50) {
                this.showNotification('info', 'Good Progress', message + '. Keep going!', 'thumbs-up');
            }
        },

        // Notification preferences management
        setupNotificationPreferences: function () {
            var self = this;
            
            // Load saved preferences
            this._loadNotificationPreferences();
            
            // Handle form submission
            $('#notification-preferences-form').on('submit', function(e) {
                e.preventDefault();
                self._saveNotificationPreferences();
            });
            
            // Handle test notifications
            $('#test-notifications').on('click', function(e) {
                e.preventDefault();
                self._testNotifications();
            });
        },

        _loadNotificationPreferences: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/notifications/preferences', 'call')
                .then(function(result) {
                    if (result.success) {
                        self._populatePreferencesForm(result.preferences);
                    }
                })
                .catch(function(error) {
                    console.error('Error loading notification preferences:', error);
                });
        },

        _populatePreferencesForm: function (preferences) {
            // Populate form with saved preferences
            Object.keys(preferences).forEach(function(key) {
                var $element = $('#' + key);
                if ($element.length) {
                    if ($element.is(':checkbox')) {
                        $element.prop('checked', preferences[key]);
                    } else {
                        $element.val(preferences[key]);
                    }
                }
            });
        },

        _saveNotificationPreferences: function () {
            var self = this;
            var preferences = {
                notify_app_status: $('#notify-app-status').is(':checked'),
                notify_documents: $('#notify-documents').is(':checked'),
                notify_deadlines: $('#notify-deadlines').is(':checked'),
                email_status: $('#email-status').is(':checked'),
                email_reminders: $('#email-reminders').is(':checked'),
                email_weekly: $('#email-weekly').is(':checked'),
                sms_urgent: $('#sms-urgent').is(':checked'),
                sms_approval: $('#sms-approval').is(':checked'),
                notification_frequency: $('#notification-frequency').val()
            };
            
            ajax.jsonRpc('/admission/notifications/preferences/save', 'call', {
                preferences: preferences
            }).then(function(result) {
                if (result.success) {
                    self.showNotification('success', 'Preferences Saved', 'Your notification preferences have been updated successfully.', 'check-circle');
                } else {
                    self.showNotification('error', 'Save Failed', 'There was an error saving your preferences. Please try again.', 'exclamation-triangle');
                }
            }).catch(function(error) {
                console.error('Error saving notification preferences:', error);
                self.showNotification('error', 'Save Failed', 'There was an error saving your preferences. Please try again.', 'exclamation-triangle');
            });
        },

        _testNotifications: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/notifications/test', 'call')
                .then(function(result) {
                    if (result.success) {
                        self.showNotification('success', 'Test Sent', 'Test notifications have been sent to your registered email and phone.', 'paper-plane');
                    } else {
                        self.showNotification('error', 'Test Failed', 'There was an error sending test notifications. Please check your contact information.', 'exclamation-triangle');
                    }
                })
                .catch(function(error) {
                    console.error('Error sending test notifications:', error);
                    self.showNotification('error', 'Test Failed', 'There was an error sending test notifications. Please try again later.', 'exclamation-triangle');
                });
        },

        // Communication system
        setupCommunicationSystem: function () {
            var self = this;
            
            // Handle add comment button
            $('#add-comment').on('click', function(e) {
                e.preventDefault();
                self._showCommentModal();
            });
            
            // Load communication history
            this._loadCommunicationHistory();
        },

        _showCommentModal: function () {
            var self = this;
            var modal = $('<div class="comment-modal">' +
                '<div class="comment-modal-content">' +
                    '<div class="comment-modal-header">' +
                        '<h5>Add Comment</h5>' +
                        '<button class="btn-close-modal">&times;</button>' +
                    '</div>' +
                    '<div class="comment-modal-body">' +
                        '<form id="comment-form">' +
                            '<div class="mb-3">' +
                                '<label for="comment-type" class="form-label">Comment Type</label>' +
                                '<select class="form-select" id="comment-type" required>' +
                                    '<option value="question">Question</option>' +
                                    '<option value="concern">Concern</option>' +
                                    '<option value="update">Status Update Request</option>' +
                                    '<option value="other">Other</option>' +
                                '</select>' +
                            '</div>' +
                            '<div class="mb-3">' +
                                '<label for="comment-message" class="form-label">Message</label>' +
                                '<textarea class="form-control" id="comment-message" rows="4" required placeholder="Please describe your comment or question..."></textarea>' +
                            '</div>' +
                        '</form>' +
                    '</div>' +
                    '<div class="comment-modal-footer">' +
                        '<button type="button" class="acmst-btn acmst-btn-secondary" id="cancel-comment">Cancel</button>' +
                        '<button type="button" class="acmst-btn acmst-btn-primary" id="submit-comment">Submit Comment</button>' +
                    '</div>' +
                '</div>' +
            '</div>');
            
            $('body').append(modal);
            
            // Handle modal events
            modal.find('.btn-close-modal, #cancel-comment').on('click', function() {
                modal.remove();
            });
            
            modal.find('#submit-comment').on('click', function() {
                self._submitComment(modal);
            });
            
            modal.on('click', function(e) {
                if (e.target === modal[0]) {
                    modal.remove();
                }
            });
        },

        _submitComment: function (modal) {
            var self = this;
            var type = modal.find('#comment-type').val();
            var message = modal.find('#comment-message').val();
            
            if (!message.trim()) {
                self.showNotification('error', 'Validation Error', 'Please enter a message.', 'exclamation-triangle');
                return;
            }
            
            ajax.jsonRpc('/admission/communication/add', 'call', {
                type: type,
                message: message
            }).then(function(result) {
                if (result.success) {
                    self.showNotification('success', 'Comment Added', 'Your comment has been submitted successfully.', 'check-circle');
                    modal.remove();
                    self._loadCommunicationHistory();
                } else {
                    self.showNotification('error', 'Submission Failed', 'There was an error submitting your comment. Please try again.', 'exclamation-triangle');
                }
            }).catch(function(error) {
                console.error('Error submitting comment:', error);
                self.showNotification('error', 'Submission Failed', 'There was an error submitting your comment. Please try again.', 'exclamation-triangle');
            });
        },

        _loadCommunicationHistory: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/communication/history', 'call')
                .then(function(result) {
                    if (result.success) {
                        self._displayCommunicationHistory(result.communications);
                    }
                })
                .catch(function(error) {
                    console.error('Error loading communication history:', error);
                });
        },

        _displayCommunicationHistory: function (communications) {
            var $container = $('#communication-history');
            $container.empty();
            
            if (communications.length === 0) {
                $container.html('<div class="text-center text-muted py-4">No communications yet.</div>');
                return;
            }
            
            communications.forEach(function(comm) {
                var $item = $('<div class="communication-item">' +
                    '<div class="communication-icon">' +
                        '<i class="fa fa-' + (comm.icon || 'comment') + '"></i>' +
                    '</div>' +
                    '<div class="communication-content">' +
                        '<div class="communication-title">' + comm.title + '</div>' +
                        '<div class="communication-message">' + comm.message + '</div>' +
                        '<div class="communication-meta">' +
                            '<span class="communication-author">' + comm.author + '</span>' +
                            '<span class="communication-time">' + comm.timestamp + '</span>' +
                        '</div>' +
                    '</div>' +
                '</div>');
                
                $container.append($item);
            });
        },

        // Health Check Portal functionality
        setupHealthCheckPortal: function () {
            var self = this;
            
            // BMI Calculator
            this._setupBMICalculator();
            
            // Appointment booking
            this._setupAppointmentBooking();
            
            // Form validation
            this._setupHealthFormValidation();
            
            // Progress tracking
            this._updateHealthProgress();
        },

        _setupBMICalculator: function () {
            var self = this;
            
            $('#height, #weight').on('input', function() {
                var height = parseFloat($('#height').val());
                var weight = parseFloat($('#weight').val());
                
                if (height && weight && height > 0 && weight > 0) {
                    var bmi = weight / Math.pow(height / 100, 2);
                    var bmiRounded = Math.round(bmi * 10) / 10;
                    
                    $('#bmi').val(bmiRounded);
                    
                    // Add BMI calculator display if it doesn't exist
                    if (!$('.bmi-calculator').length) {
                        var bmiCategory = self._getBMICategory(bmi);
                        var $bmiDisplay = $('<div class="bmi-calculator">' +
                            '<div class="bmi-result">BMI: ' + bmiRounded + '</div>' +
                            '<div class="bmi-category">Category: ' + bmiCategory + '</div>' +
                        '</div>');
                        
                        $('#weight').closest('.acmst-form-group').after($bmiDisplay);
                    } else {
                        var bmiCategory = self._getBMICategory(bmi);
                        $('.bmi-result').text('BMI: ' + bmiRounded);
                        $('.bmi-category').text('Category: ' + bmiCategory);
                    }
                }
            });
        },

        _getBMICategory: function (bmi) {
            if (bmi < 18.5) return 'Underweight';
            if (bmi < 25) return 'Normal weight';
            if (bmi < 30) return 'Overweight';
            return 'Obese';
        },

        _setupAppointmentBooking: function () {
            var self = this;
            
            $('#book-appointment').on('click', function(e) {
                e.preventDefault();
                self._bookAppointment();
            });
        },

        _bookAppointment: function () {
            var self = this;
            var selectedSlot = $('input[name="appointment_slot"]:checked').val();
            
            if (!selectedSlot) {
                self._getNotificationSystem().showNotification('error', 'No Slot Selected', 'Please select an appointment time.', 'exclamation-triangle');
                return;
            }
            
            ajax.jsonRpc('/admission/health-check/book-appointment', 'call', {
                slot: selectedSlot
            }).then(function(result) {
                if (result.success) {
                    self._getNotificationSystem().showNotification('success', 'Appointment Booked', 'Your appointment has been scheduled successfully.', 'calendar-check');
                    self._updateHealthProgress();
                } else {
                    self._getNotificationSystem().showNotification('error', 'Booking Failed', 'There was an error booking your appointment. Please try again.', 'exclamation-triangle');
                }
            }).catch(function(error) {
                console.error('Error booking appointment:', error);
                self._getNotificationSystem().showNotification('error', 'Booking Failed', 'There was an error booking your appointment. Please try again.', 'exclamation-triangle');
            });
        },

        _setupHealthFormValidation: function () {
            var self = this;
            
            // Height validation
            $('#height').on('input', function() {
                var height = parseFloat($(this).val());
                if (height && (height < 100 || height > 250)) {
                    self._showFieldError($(this), 'Height must be between 100-250 cm');
                } else {
                    self._clearFieldError($(this));
                }
            });
            
            // Weight validation
            $('#weight').on('input', function() {
                var weight = parseFloat($(this).val());
                if (weight && (weight < 30 || weight > 200)) {
                    self._showFieldError($(this), 'Weight must be between 30-200 kg');
                } else {
                    self._clearFieldError($(this));
                }
            });
            
            // Phone validation for emergency contact
            $('input[name="emergency_contact_phone"]').on('input', function() {
                var phone = $(this).val();
                if (phone && !self._validatePhone(phone)) {
                    self._showFieldError($(this), 'Please enter a valid phone number');
                } else {
                    self._clearFieldError($(this));
                }
            });
        },

        _updateHealthProgress: function () {
            // Update progress steps based on current state
            var currentState = $('.health-status-badge').attr('class').match(/health-status-(\w+)/);
            if (currentState) {
                var state = currentState[1];
                
                // Reset all steps
                $('.progress-step').removeClass('completed active');
                
                // Mark completed steps
                if (state !== 'pending') {
                    $('.progress-step').first().addClass('completed');
                }
                
                if (['appointment_scheduled', 'appointment_completed', 'approved', 'rejected'].includes(state)) {
                    $('.progress-step').eq(1).addClass('completed');
                }
                
                if (['appointment_completed', 'approved', 'rejected'].includes(state)) {
                    $('.progress-step').eq(2).addClass('completed');
                }
                
                if (['approved', 'rejected'].includes(state)) {
                    $('.progress-step').eq(3).addClass('completed');
                }
                
                // Mark active step
                if (state === 'form_completed') {
                    $('.progress-step').eq(1).addClass('active');
                } else if (state === 'appointment_scheduled') {
                    $('.progress-step').eq(2).addClass('active');
                } else if (state === 'appointment_completed') {
                    $('.progress-step').eq(3).addClass('active');
                }
            }
        },

        // Conditions Portal functionality
        setupConditionsPortal: function () {
            var self = this;
            
            // Load conditions data
            this._loadConditionsData();
            
            // Setup event handlers
            this._setupConditionsEventHandlers();
            
            // Setup filtering
            this._setupConditionsFiltering();
            
            // Setup deadline tracking
            this._setupDeadlineTracking();
        },

        _loadConditionsData: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/conditions/list', 'call')
                .then(function(result) {
                    if (result.success) {
                        self._displayConditions(result.conditions);
                        self._updateConditionsStats(result.stats);
                    }
                })
                .catch(function(error) {
                    console.error('Error loading conditions:', error);
                });
        },

        _displayConditions: function (conditions) {
            var $container = $('#conditions-list');
            $container.empty();
            
            if (conditions.length === 0) {
                $container.html('<div class="text-center text-muted py-4">No conditions found.</div>');
                return;
            }
            
            conditions.forEach(function(condition) {
                var $condition = self._createConditionItem(condition);
                $container.append($condition);
            });
        },

        _createConditionItem: function (condition) {
            var self = this;
            var statusClass = 'status-' + condition.status;
            var priorityClass = condition.priority || 'medium';
            
            var $condition = $('<div class="condition-item" data-condition-id="' + condition.id + '">' +
                '<div class="condition-header">' +
                    '<div class="condition-title">' +
                        '<h5>' + condition.title + '</h5>' +
                        '<span class="condition-type">' + condition.type + '</span>' +
                    '</div>' +
                    '<div class="condition-status">' +
                        '<span class="status-badge ' + statusClass + '">' + condition.status + '</span>' +
                    '</div>' +
                '</div>' +
                '<div class="condition-content">' +
                    '<p class="condition-description">' + condition.description + '</p>' +
                    '<div class="condition-details">' +
                        '<div class="detail-row">' +
                            '<span class="detail-label">Deadline:</span>' +
                            '<span class="detail-value deadline">' + condition.deadline + '</span>' +
                        '</div>' +
                        '<div class="detail-row">' +
                            '<span class="detail-label">Priority:</span>' +
                            '<span class="detail-value priority ' + priorityClass + '">' + condition.priority + '</span>' +
                        '</div>' +
                        '<div class="detail-row">' +
                            '<span class="detail-label">Documents Required:</span>' +
                            '<span class="detail-value">' + condition.documents_required + '</span>' +
                        '</div>' +
                    '</div>' +
                    '<div class="condition-actions">' +
                        '<button class="acmst-btn acmst-btn-primary acmst-btn-sm" data-action="upload-documents" data-condition-id="' + condition.id + '">' +
                            '<i class="fa fa-upload"></i> Upload Documents' +
                        '</button>' +
                        '<button class="acmst-btn acmst-btn-outline acmst-btn-sm" data-action="view-details" data-condition-id="' + condition.id + '">' +
                            '<i class="fa fa-eye"></i> View Details' +
                        '</button>' +
                    '</div>' +
                '</div>' +
            '</div>');
            
            return $condition;
        },

        _updateConditionsStats: function (stats) {
            $('.stat-item.completed .stat-number').text(stats.completed || 0);
            $('.stat-item.pending .stat-number').text(stats.pending || 0);
            $('.stat-item.overdue .stat-number').text(stats.overdue || 0);
            
            // Update progress bar
            var progress = stats.progress || 0;
            $('.progress-bar-large .progress-fill').css('width', progress + '%');
            $('.progress-percentage').text(progress + '%');
            
            // Update progress details
            $('.detail-item .detail-value').eq(0).text(stats.total || 0);
            $('.detail-item .detail-value.completed').text(stats.completed || 0);
            $('.detail-item .detail-value.pending').text((stats.total || 0) - (stats.completed || 0));
        },

        _setupConditionsEventHandlers: function () {
            var self = this;
            
            // Refresh conditions
            $('#refresh-conditions').on('click', function(e) {
                e.preventDefault();
                self._loadConditionsData();
            });
            
            // Upload documents
            $(document).on('click', '[data-action="upload-documents"]', function(e) {
                e.preventDefault();
                var conditionId = $(this).data('condition-id');
                self._showUploadModal(conditionId);
            });
            
            // View details
            $(document).on('click', '[data-action="view-details"]', function(e) {
                e.preventDefault();
                var conditionId = $(this).data('condition-id');
                self._showConditionDetails(conditionId);
            });
            
            // Quick actions
            $('#upload-documents').on('click', function(e) {
                e.preventDefault();
                self._showUploadModal();
            });
            
            $('#view-guidance').on('click', function(e) {
                e.preventDefault();
                self._showGuidanceModal();
            });
            
            $('#contact-support').on('click', function(e) {
                e.preventDefault();
                self._showSupportModal();
            });
        },

        _setupConditionsFiltering: function () {
            var self = this;
            
            $('#condition-filter').on('change', function() {
                var filter = $(this).val();
                self._filterConditions(filter);
            });
        },

        _filterConditions: function (filter) {
            var $conditions = $('.condition-item');
            
            if (filter === 'all') {
                $conditions.show();
            } else {
                $conditions.hide();
                $conditions.filter('[data-status="' + filter + '"]').show();
            }
        },

        _setupDeadlineTracking: function () {
            var self = this;
            
            // Check for overdue conditions
            this._checkOverdueConditions();
            
            // Set up periodic deadline checks
            setInterval(function() {
                self._checkOverdueConditions();
            }, 60000); // Check every minute
        },

        _checkOverdueConditions: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/conditions/check-deadlines', 'call')
                .then(function(result) {
                    if (result.success && result.overdue_conditions.length > 0) {
                        result.overdue_conditions.forEach(function(condition) {
                            self._getNotificationSystem().showNotification(
                                'warning',
                                'Deadline Approaching',
                                condition.title + ' is due in ' + condition.days_remaining + ' days',
                                'exclamation-triangle'
                            );
                        });
                    }
                })
                .catch(function(error) {
                    console.error('Error checking deadlines:', error);
                });
        },

        _showUploadModal: function (conditionId) {
            var self = this;
            var modal = $('<div class="comment-modal">' +
                '<div class="comment-modal-content">' +
                    '<div class="comment-modal-header">' +
                        '<h5>Upload Documents</h5>' +
                        '<button class="btn-close-modal">&times;</button>' +
                    '</div>' +
                    '<div class="comment-modal-body">' +
                        '<form id="document-upload-form" enctype="multipart/form-data">' +
                            '<div class="mb-3">' +
                                '<label for="document-files" class="form-label">Select Documents</label>' +
                                '<input type="file" class="form-control" id="document-files" multiple accept=".pdf,.doc,.docx,.jpg,.jpeg,.png">' +
                            '</div>' +
                            '<div class="mb-3">' +
                                '<label for="document-notes" class="form-label">Notes (Optional)</label>' +
                                '<textarea class="form-control" id="document-notes" rows="3" placeholder="Add any additional notes about these documents..."></textarea>' +
                            '</div>' +
                        '</form>' +
                    '</div>' +
                    '<div class="comment-modal-footer">' +
                        '<button type="button" class="acmst-btn acmst-btn-secondary" id="cancel-upload">Cancel</button>' +
                        '<button type="button" class="acmst-btn acmst-btn-primary" id="submit-upload">Upload Documents</button>' +
                    '</div>' +
                '</div>' +
            '</div>');
            
            $('body').append(modal);
            
            // Handle modal events
            modal.find('.btn-close-modal, #cancel-upload').on('click', function() {
                modal.remove();
            });
            
            modal.find('#submit-upload').on('click', function() {
                self._submitDocuments(modal, conditionId);
            });
            
            modal.on('click', function(e) {
                if (e.target === modal[0]) {
                    modal.remove();
                }
            });
        },

        _submitDocuments: function (modal, conditionId) {
            var self = this;
            var formData = new FormData();
            var files = modal.find('#document-files')[0].files;
            var notes = modal.find('#document-notes').val();
            
            if (files.length === 0) {
                self._getNotificationSystem().showNotification('error', 'No Files Selected', 'Please select at least one document to upload.', 'exclamation-triangle');
                return;
            }
            
            for (var i = 0; i < files.length; i++) {
                formData.append('documents', files[i]);
            }
            formData.append('notes', notes);
            formData.append('condition_id', conditionId);
            
            // Show loading state
            modal.find('#submit-upload').prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> Uploading...');
            
            ajax.jsonRpc('/admission/conditions/upload-documents', 'call', formData)
                .then(function(result) {
                    if (result.success) {
                        self._getNotificationSystem().showNotification('success', 'Documents Uploaded', 'Your documents have been uploaded successfully.', 'check-circle');
                        modal.remove();
                        self._loadConditionsData();
                    } else {
                        self._getNotificationSystem().showNotification('error', 'Upload Failed', 'There was an error uploading your documents. Please try again.', 'exclamation-triangle');
                    }
                })
                .catch(function(error) {
                    console.error('Error uploading documents:', error);
                    self._getNotificationSystem().showNotification('error', 'Upload Failed', 'There was an error uploading your documents. Please try again.', 'exclamation-triangle');
                })
                .finally(function() {
                    modal.find('#submit-upload').prop('disabled', false).html('Upload Documents');
                });
        },

        _showGuidanceModal: function () {
            var self = this;
            var modal = $('<div class="comment-modal">' +
                '<div class="comment-modal-content" style="max-width: 800px;">' +
                    '<div class="comment-modal-header">' +
                        '<h5>Step-by-Step Guidance</h5>' +
                        '<button class="btn-close-modal">&times;</button>' +
                    '</div>' +
                    '<div class="comment-modal-body">' +
                        '<div class="guidance-content">' +
                            '<h6>How to Complete Your Conditions:</h6>' +
                            '<ol>' +
                                '<li><strong>Review Requirements:</strong> Carefully read each condition and understand what documents or actions are required.</li>' +
                                '<li><strong>Gather Documents:</strong> Collect all necessary documents as specified in each condition.</li>' +
                                '<li><strong>Upload Documents:</strong> Use the upload button to submit your documents for each condition.</li>' +
                                '<li><strong>Track Progress:</strong> Monitor your progress and upcoming deadlines in the dashboard.</li>' +
                                '<li><strong>Follow Up:</strong> Check for any feedback or additional requirements from the admissions office.</li>' +
                            '</ol>' +
                            '<h6>Tips for Success:</h6>' +
                            '<ul>' +
                                '<li>Submit documents well before deadlines</li>' +
                                '<li>Ensure all documents are clear and legible</li>' +
                                '<li>Keep copies of all submitted documents</li>' +
                                '<li>Contact support if you have any questions</li>' +
                            '</ul>' +
                        '</div>' +
                    '</div>' +
                    '<div class="comment-modal-footer">' +
                        '<button type="button" class="acmst-btn acmst-btn-primary" id="close-guidance">Got It</button>' +
                    '</div>' +
                '</div>' +
            '</div>');
            
            $('body').append(modal);
            
            // Handle modal events
            modal.find('.btn-close-modal, #close-guidance').on('click', function() {
                modal.remove();
            });
            
            modal.on('click', function(e) {
                if (e.target === modal[0]) {
                    modal.remove();
                }
            });
        },

        _showSupportModal: function () {
            var self = this;
            var modal = $('<div class="comment-modal">' +
                '<div class="comment-modal-content">' +
                    '<div class="comment-modal-header">' +
                        '<h5>Contact Support</h5>' +
                        '<button class="btn-close-modal">&times;</button>' +
                    '</div>' +
                    '<div class="comment-modal-body">' +
                        '<form id="support-form">' +
                            '<div class="mb-3">' +
                                '<label for="support-subject" class="form-label">Subject</label>' +
                                '<input type="text" class="form-control" id="support-subject" required placeholder="Brief description of your question">' +
                            '</div>' +
                            '<div class="mb-3">' +
                                '<label for="support-message" class="form-label">Message</label>' +
                                '<textarea class="form-control" id="support-message" rows="4" required placeholder="Please describe your question or issue in detail..."></textarea>' +
                            '</div>' +
                            '<div class="mb-3">' +
                                '<label for="support-priority" class="form-label">Priority</label>' +
                                '<select class="form-select" id="support-priority">' +
                                    '<option value="low">Low</option>' +
                                    '<option value="medium" selected>Medium</option>' +
                                    '<option value="high">High</option>' +
                                '</select>' +
                            '</div>' +
                        '</form>' +
                    '</div>' +
                    '<div class="comment-modal-footer">' +
                        '<button type="button" class="acmst-btn acmst-btn-secondary" id="cancel-support">Cancel</button>' +
                        '<button type="button" class="acmst-btn acmst-btn-primary" id="submit-support">Send Message</button>' +
                    '</div>' +
                '</div>' +
            '</div>');
            
            $('body').append(modal);
            
            // Handle modal events
            modal.find('.btn-close-modal, #cancel-support').on('click', function() {
                modal.remove();
            });
            
            modal.find('#submit-support').on('click', function() {
                self._submitSupportRequest(modal);
            });
            
            modal.on('click', function(e) {
                if (e.target === modal[0]) {
                    modal.remove();
                }
            });
        },

        _submitSupportRequest: function (modal) {
            var self = this;
            var subject = modal.find('#support-subject').val();
            var message = modal.find('#support-message').val();
            var priority = modal.find('#support-priority').val();
            
            if (!subject || !message) {
                self._getNotificationSystem().showNotification('error', 'Validation Error', 'Please fill in all required fields.', 'exclamation-triangle');
                return;
            }
            
            ajax.jsonRpc('/admission/support/submit', 'call', {
                subject: subject,
                message: message,
                priority: priority
            }).then(function(result) {
                if (result.success) {
                    self._getNotificationSystem().showNotification('success', 'Message Sent', 'Your support request has been submitted successfully.', 'check-circle');
                    modal.remove();
                } else {
                    self._getNotificationSystem().showNotification('error', 'Submission Failed', 'There was an error submitting your request. Please try again.', 'exclamation-triangle');
                }
            }).catch(function(error) {
                console.error('Error submitting support request:', error);
                self._getNotificationSystem().showNotification('error', 'Submission Failed', 'There was an error submitting your request. Please try again.', 'exclamation-triangle');
            });
        },

        // Document Management Portal functionality
        setupDocumentManagement: function () {
            var self = this;
            
            // Load documents data
            this._loadDocumentsData();
            
            // Setup event handlers
            this._setupDocumentEventHandlers();
            
            // Setup filtering and search
            this._setupDocumentFiltering();
            
            // Setup view controls
            this._setupViewControls();
        },

        _loadDocumentsData: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/documents/list', 'call')
                .then(function(result) {
                    if (result.success) {
                        self._displayDocuments(result.documents);
                        self._updateDocumentStats(result.stats);
                    }
                })
                .catch(function(error) {
                    console.error('Error loading documents:', error);
                });
        },

        _displayDocuments: function (documents) {
            var $container = $('#document-list');
            $container.empty();
            
            if (documents.length === 0) {
                $container.html('<div class="text-center text-muted py-4">No documents found.</div>');
                return;
            }
            
            documents.forEach(function(doc) {
                var $document = self._createDocumentItem(doc);
                $container.append($document);
            });
        },

        _createDocumentItem: function (doc) {
            var self = this;
            var statusClass = 'status-' + doc.status;
            var fileIcon = self._getFileIcon(doc.file_type);
            
            var $document = $('<div class="document-item" data-document-id="' + doc.id + '" data-category="' + doc.category + '">' +
                '<div class="document-icon">' +
                    '<i class="fa ' + fileIcon + '"></i>' +
                '</div>' +
                '<div class="document-info">' +
                    '<div class="document-name">' + doc.name + '</div>' +
                    '<div class="document-meta">' +
                        '<span class="document-size">' + doc.size + '</span>' +
                        '<span class="document-date">' + doc.upload_date + '</span>' +
                        '<span class="document-status ' + statusClass + '">' + doc.status + '</span>' +
                    '</div>' +
                '</div>' +
                '<div class="document-actions">' +
                    '<button class="btn btn-sm btn-outline-primary" data-action="preview" data-document-id="' + doc.id + '">' +
                        '<i class="fa fa-eye"></i>' +
                    '</button>' +
                    '<button class="btn btn-sm btn-outline-secondary" data-action="download" data-document-id="' + doc.id + '">' +
                        '<i class="fa fa-download"></i>' +
                    '</button>' +
                    '<button class="btn btn-sm btn-outline-danger" data-action="delete" data-document-id="' + doc.id + '">' +
                        '<i class="fa fa-trash"></i>' +
                    '</button>' +
                '</div>' +
            '</div>');
            
            return $document;
        },

        _getFileIcon: function (fileType) {
            var type = fileType.toLowerCase();
            if (type.includes('pdf')) return 'fa-file-pdf';
            if (type.includes('word') || type.includes('doc')) return 'fa-file-word';
            if (type.includes('image') || type.includes('jpg') || type.includes('jpeg') || type.includes('png')) return 'fa-file-image';
            if (type.includes('excel') || type.includes('xls')) return 'fa-file-excel';
            if (type.includes('powerpoint') || type.includes('ppt')) return 'fa-file-powerpoint';
            return 'fa-file';
        },

        _updateDocumentStats: function (stats) {
            $('.stat-item.total .stat-number').text(stats.total || 0);
            $('.stat-item.approved .stat-number').text(stats.approved || 0);
            $('.stat-item.pending .stat-number').text(stats.pending || 0);
            
            // Update category counts
            $('.category-item[data-category="all"] .count').text(stats.total || 0);
            $('.category-item[data-category="academic"] .count').text(stats.academic || 0);
            $('.category-item[data-category="financial"] .count').text(stats.financial || 0);
            $('.category-item[data-category="health"] .count').text(stats.health || 0);
            $('.category-item[data-category="identity"] .count').text(stats.identity || 0);
        },

        _setupDocumentEventHandlers: function () {
            var self = this;
            
            // Category filtering
            $('.category-item').on('click', function() {
                var category = $(this).data('category');
                self._filterDocumentsByCategory(category);
                $('.category-item').removeClass('active');
                $(this).addClass('active');
            });
            
            // Document actions
            $(document).on('click', '[data-action="preview"]', function(e) {
                e.preventDefault();
                var documentId = $(this).data('document-id');
                self._previewDocument(documentId);
            });
            
            $(document).on('click', '[data-action="download"]', function(e) {
                e.preventDefault();
                var documentId = $(this).data('document-id');
                self._downloadDocument(documentId);
            });
            
            $(document).on('click', '[data-action="delete"]', function(e) {
                e.preventDefault();
                var documentId = $(this).data('document-id');
                self._deleteDocument(documentId);
            });
            
            // Quick actions
            $('#bulk-upload').on('click', function(e) {
                e.preventDefault();
                self._showBulkUploadModal();
            });
            
            $('#create-folder').on('click', function(e) {
                e.preventDefault();
                self._createFolder();
            });
            
            $('#download-all').on('click', function(e) {
                e.preventDefault();
                self._downloadAllDocuments();
            });
        },

        _setupDocumentFiltering: function () {
            var self = this;
            
            // Search functionality
            $('#document-search').on('input', function() {
                var searchTerm = $(this).val().toLowerCase();
                self._searchDocuments(searchTerm);
            });
            
            // Sort functionality
            $('#sort-documents').on('change', function() {
                var sortBy = $(this).val();
                self._sortDocuments(sortBy);
            });
        },

        _setupViewControls: function () {
            var self = this;
            
            $('#grid-view').on('click', function() {
                $('#document-list').addClass('grid-view');
                $('#list-view').removeClass('active');
                $(this).addClass('active');
            });
            
            $('#list-view').on('click', function() {
                $('#document-list').removeClass('grid-view');
                $('#grid-view').removeClass('active');
                $(this).addClass('active');
            });
        },

        _filterDocumentsByCategory: function (category) {
            var $documents = $('.document-item');
            
            if (category === 'all') {
                $documents.show();
            } else {
                $documents.hide();
                $documents.filter('[data-category="' + category + '"]').show();
            }
        },

        _searchDocuments: function (searchTerm) {
            var $documents = $('.document-item');
            
            $documents.each(function() {
                var $doc = $(this);
                var docName = $doc.find('.document-name').text().toLowerCase();
                
                if (docName.includes(searchTerm)) {
                    $doc.show();
                } else {
                    $doc.hide();
                }
            });
        },

        _sortDocuments: function (sortBy) {
            var $container = $('#document-list');
            var $documents = $container.find('.document-item').toArray();
            
            $documents.sort(function(a, b) {
                var $a = $(a);
                var $b = $(b);
                
                switch (sortBy) {
                    case 'name':
                        return $a.find('.document-name').text().localeCompare($b.find('.document-name').text());
                    case 'date':
                        return new Date($b.data('date')) - new Date($a.data('date'));
                    case 'size':
                        return $b.data('size') - $a.data('size');
                    case 'status':
                        return $a.find('.document-status').text().localeCompare($b.find('.document-status').text());
                    default:
                        return 0;
                }
            });
            
            $container.empty().append($documents);
        },

        _previewDocument: function (documentId) {
            var self = this;
            
            ajax.jsonRpc('/admission/documents/preview', 'call', {
                document_id: documentId
            }).then(function(result) {
                if (result.success) {
                    self._showDocumentPreviewModal(result.document);
                } else {
                    self._getNotificationSystem().showNotification('error', 'Preview Error', 'Could not load document preview.', 'exclamation-triangle');
                }
            }).catch(function(error) {
                console.error('Error loading document preview:', error);
                self._getNotificationSystem().showNotification('error', 'Preview Error', 'Could not load document preview.', 'exclamation-triangle');
            });
        },

        _showDocumentPreviewModal: function (document) {
            var self = this;
            var modal = $('<div class="document-preview-modal">' +
                '<div class="document-preview-content">' +
                    '<div class="document-preview-header">' +
                        '<h5>' + document.name + '</h5>' +
                        '<button class="btn-close-modal">&times;</button>' +
                    '</div>' +
                    '<div class="document-preview-body">' +
                        '<iframe src="' + document.preview_url + '"></iframe>' +
                    '</div>' +
                '</div>' +
            '</div>');
            
            $('body').append(modal);
            
            // Handle modal events
            modal.find('.btn-close-modal').on('click', function() {
                modal.remove();
            });
            
            modal.on('click', function(e) {
                if (e.target === modal[0]) {
                    modal.remove();
                }
            });
        },

        _downloadDocument: function (documentId) {
            window.open('/admission/documents/download/' + documentId, '_blank');
        },

        _deleteDocument: function (documentId) {
            var self = this;
            
            if (confirm('Are you sure you want to delete this document?')) {
                ajax.jsonRpc('/admission/documents/delete', 'call', {
                    document_id: documentId
                }).then(function(result) {
                    if (result.success) {
                        self._getNotificationSystem().showNotification('success', 'Document Deleted', 'The document has been deleted successfully.', 'check-circle');
                        self._loadDocumentsData();
                    } else {
                        self._getNotificationSystem().showNotification('error', 'Delete Failed', 'There was an error deleting the document.', 'exclamation-triangle');
                    }
                }).catch(function(error) {
                    console.error('Error deleting document:', error);
                    self._getNotificationSystem().showNotification('error', 'Delete Failed', 'There was an error deleting the document.', 'exclamation-triangle');
                });
            }
        },

        _showBulkUploadModal: function () {
            var self = this;
            var modal = $('<div class="bulk-upload-modal">' +
                '<div class="bulk-upload-content">' +
                    '<div class="bulk-upload-header">' +
                        '<h5>Bulk Upload Documents</h5>' +
                        '<button class="btn-close-modal">&times;</button>' +
                    '</div>' +
                    '<div class="bulk-upload-body">' +
                        '<div class="upload-zone" id="upload-zone">' +
                            '<i class="fa fa-cloud-upload-alt"></i>' +
                            '<h6>Drag and drop files here or click to select</h6>' +
                            '<p>Supported formats: PDF, DOC, DOCX, JPG, PNG (Max 10MB each)</p>' +
                            '<input type="file" id="bulk-file-input" multiple accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" style="display: none;">' +
                        '</div>' +
                        '<div class="upload-progress" id="upload-progress" style="display: none;">' +
                            '<h6>Upload Progress</h6>' +
                            '<div id="progress-list"></div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="comment-modal-footer">' +
                        '<button type="button" class="acmst-btn acmst-btn-secondary" id="cancel-bulk-upload">Cancel</button>' +
                        '<button type="button" class="acmst-btn acmst-btn-primary" id="start-upload" disabled>Start Upload</button>' +
                    '</div>' +
                '</div>' +
            '</div>');
            
            $('body').append(modal);
            
            // Setup drag and drop
            self._setupBulkUploadDragDrop(modal);
            
            // Handle modal events
            modal.find('.btn-close-modal, #cancel-bulk-upload').on('click', function() {
                modal.remove();
            });
            
            modal.find('#start-upload').on('click', function() {
                self._startBulkUpload(modal);
            });
            
            modal.on('click', function(e) {
                if (e.target === modal[0]) {
                    modal.remove();
                }
            });
        },

        _createFolder: function () {
            var self = this;
            var folderName = prompt('Enter folder name:');
            
            if (folderName) {
                ajax.jsonRpc('/admission/documents/create-folder', 'call', {
                    name: folderName
                }).then(function(result) {
                    if (result.success) {
                        self._getNotificationSystem().showNotification('success', 'Folder Created', 'The folder has been created successfully.', 'check-circle');
                        self._loadDocumentsData();
                    } else {
                        self._getNotificationSystem().showNotification('error', 'Create Failed', 'There was an error creating the folder.', 'exclamation-triangle');
                    }
                }).catch(function(error) {
                    console.error('Error creating folder:', error);
                    self._getNotificationSystem().showNotification('error', 'Create Failed', 'There was an error creating the folder.', 'exclamation-triangle');
                });
            }
        },

        _downloadAllDocuments: function () {
            window.open('/admission/documents/download-all', '_blank');
        }
    });

    // Document Management Widget
    publicWidget.registry.PortalDocumentManagement = publicWidget.Widget.extend({
        selector: '.acmst-portal-container',
        events: {
            'click #document-management-tab': '_onDocumentManagementClick',
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (self.$el.find('#document-management-tab').length) {
                    self.setupDocumentManagement();
                }
            });
        },

        setupDocumentManagement: function () {
            var self = this;
            
            // Load documents data
            this._loadDocumentsData();
            
            // Setup event handlers
            this._setupDocumentEventHandlers();
            
            // Setup filtering and search
            this._setupDocumentFiltering();
            
            // Setup view controls
            this._setupViewControls();
        },

        _loadDocumentsData: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/documents/list', 'call')
                .then(function(result) {
                    if (result.success) {
                        self._displayDocuments(result.documents);
                        self._updateDocumentStats(result.stats);
                    }
                })
                .catch(function(error) {
                    console.error('Error loading documents:', error);
                });
        },

        _displayDocuments: function (documents) {
            var $container = $('#document-list');
            $container.empty();
            
            if (documents.length === 0) {
                $container.html('<div class="text-center text-muted py-4">No documents found.</div>');
                return;
            }
            
            documents.forEach(function(doc) {
                var $document = self._createDocumentItem(doc);
                $container.append($document);
            });
        },

        _createDocumentItem: function (doc) {
            var self = this;
            var statusClass = 'status-' + doc.status;
            var fileIcon = self._getFileIcon(doc.file_type);
            
            var $document = $('<div class="document-item" data-document-id="' + doc.id + '" data-category="' + doc.category + '">' +
                '<div class="document-icon">' +
                    '<i class="fa ' + fileIcon + '"></i>' +
                '</div>' +
                '<div class="document-info">' +
                    '<div class="document-name">' + doc.name + '</div>' +
                    '<div class="document-meta">' +
                        '<span class="document-size">' + doc.size + '</span>' +
                        '<span class="document-date">' + doc.upload_date + '</span>' +
                        '<span class="document-status ' + statusClass + '">' + doc.status + '</span>' +
                    '</div>' +
                '</div>' +
                '<div class="document-actions">' +
                    '<button class="btn btn-sm btn-outline-primary" data-action="preview" data-document-id="' + doc.id + '">' +
                        '<i class="fa fa-eye"></i>' +
                    '</button>' +
                    '<button class="btn btn-sm btn-outline-secondary" data-action="download" data-document-id="' + doc.id + '">' +
                        '<i class="fa fa-download"></i>' +
                    '</button>' +
                    '<button class="btn btn-sm btn-outline-danger" data-action="delete" data-document-id="' + doc.id + '">' +
                        '<i class="fa fa-trash"></i>' +
                    '</button>' +
                '</div>' +
            '</div>');
            
            return $document;
        },

        _getFileIcon: function (fileType) {
            var type = fileType.toLowerCase();
            if (type.includes('pdf')) return 'fa-file-pdf';
            if (type.includes('word') || type.includes('doc')) return 'fa-file-word';
            if (type.includes('image') || type.includes('jpg') || type.includes('jpeg') || type.includes('png')) return 'fa-file-image';
            if (type.includes('excel') || type.includes('xls')) return 'fa-file-excel';
            if (type.includes('powerpoint') || type.includes('ppt')) return 'fa-file-powerpoint';
            return 'fa-file';
        },

        _updateDocumentStats: function (stats) {
            $('.stat-item.total .stat-number').text(stats.total || 0);
            $('.stat-item.approved .stat-number').text(stats.approved || 0);
            $('.stat-item.pending .stat-number').text(stats.pending || 0);
            
            // Update category counts
            $('.category-item[data-category="all"] .count').text(stats.total || 0);
            $('.category-item[data-category="academic"] .count').text(stats.academic || 0);
            $('.category-item[data-category="financial"] .count').text(stats.financial || 0);
            $('.category-item[data-category="health"] .count').text(stats.health || 0);
            $('.category-item[data-category="identity"] .count').text(stats.identity || 0);
        },

        _setupDocumentEventHandlers: function () {
            var self = this;
            
            // Category filtering
            $('.category-item').on('click', function() {
                var category = $(this).data('category');
                self._filterDocumentsByCategory(category);
                $('.category-item').removeClass('active');
                $(this).addClass('active');
            });
            
            // Document actions
            $(document).on('click', '[data-action="preview"]', function(e) {
                e.preventDefault();
                var documentId = $(this).data('document-id');
                self._previewDocument(documentId);
            });
            
            $(document).on('click', '[data-action="download"]', function(e) {
                e.preventDefault();
                var documentId = $(this).data('document-id');
                self._downloadDocument(documentId);
            });
            
            $(document).on('click', '[data-action="delete"]', function(e) {
                e.preventDefault();
                var documentId = $(this).data('document-id');
                self._deleteDocument(documentId);
            });
            
            // Quick actions
            $('#bulk-upload').on('click', function(e) {
                e.preventDefault();
                self._showBulkUploadModal();
            });
            
            $('#create-folder').on('click', function(e) {
                e.preventDefault();
                self._createFolder();
            });
            
            $('#download-all').on('click', function(e) {
                e.preventDefault();
                self._downloadAllDocuments();
            });
        },

        _setupDocumentFiltering: function () {
            var self = this;
            
            // Search functionality
            $('#document-search').on('input', function() {
                var searchTerm = $(this).val().toLowerCase();
                self._searchDocuments(searchTerm);
            });
            
            // Sort functionality
            $('#sort-documents').on('change', function() {
                var sortBy = $(this).val();
                self._sortDocuments(sortBy);
            });
        },

        _setupViewControls: function () {
            var self = this;
            
            $('#grid-view').on('click', function() {
                $('#document-list').addClass('grid-view');
                $('#list-view').removeClass('active');
                $(this).addClass('active');
            });
            
            $('#list-view').on('click', function() {
                $('#document-list').removeClass('grid-view');
                $('#grid-view').removeClass('active');
                $(this).addClass('active');
            });
        },

        _filterDocumentsByCategory: function (category) {
            var $documents = $('.document-item');
            
            if (category === 'all') {
                $documents.show();
            } else {
                $documents.hide();
                $documents.filter('[data-category="' + category + '"]').show();
            }
        },

        _searchDocuments: function (searchTerm) {
            var $documents = $('.document-item');
            
            $documents.each(function() {
                var $doc = $(this);
                var docName = $doc.find('.document-name').text().toLowerCase();
                
                if (docName.includes(searchTerm)) {
                    $doc.show();
                } else {
                    $doc.hide();
                }
            });
        },

        _sortDocuments: function (sortBy) {
            var $container = $('#document-list');
            var $documents = $container.find('.document-item').toArray();
            
            $documents.sort(function(a, b) {
                var $a = $(a);
                var $b = $(b);
                
                switch (sortBy) {
                    case 'name':
                        return $a.find('.document-name').text().localeCompare($b.find('.document-name').text());
                    case 'date':
                        return new Date($b.data('date')) - new Date($a.data('date'));
                    case 'size':
                        return $b.data('size') - $a.data('size');
                    case 'status':
                        return $a.find('.document-status').text().localeCompare($b.find('.document-status').text());
                    default:
                        return 0;
                }
            });
            
            $container.empty().append($documents);
        },

        _previewDocument: function (documentId) {
            var self = this;
            
            ajax.jsonRpc('/admission/documents/preview', 'call', {
                document_id: documentId
            }).then(function(result) {
                if (result.success) {
                    self._showDocumentPreviewModal(result.document);
                } else {
                    self._getNotificationSystem().showNotification('error', 'Preview Error', 'Could not load document preview.', 'exclamation-triangle');
                }
            }).catch(function(error) {
                console.error('Error loading document preview:', error);
                self._getNotificationSystem().showNotification('error', 'Preview Error', 'Could not load document preview.', 'exclamation-triangle');
            });
        },

        _showDocumentPreviewModal: function (document) {
            var self = this;
            var modal = $('<div class="document-preview-modal">' +
                '<div class="document-preview-content">' +
                    '<div class="document-preview-header">' +
                        '<h5>' + document.name + '</h5>' +
                        '<button class="btn-close-modal">&times;</button>' +
                    '</div>' +
                    '<div class="document-preview-body">' +
                        '<iframe src="' + document.preview_url + '"></iframe>' +
                    '</div>' +
                '</div>' +
            '</div>');
            
            $('body').append(modal);
            
            // Handle modal events
            modal.find('.btn-close-modal').on('click', function() {
                modal.remove();
            });
            
            modal.on('click', function(e) {
                if (e.target === modal[0]) {
                    modal.remove();
                }
            });
        },

        _downloadDocument: function (documentId) {
            window.open('/admission/documents/download/' + documentId, '_blank');
        },

        _deleteDocument: function (documentId) {
            var self = this;
            
            if (confirm('Are you sure you want to delete this document?')) {
                ajax.jsonRpc('/admission/documents/delete', 'call', {
                    document_id: documentId
                }).then(function(result) {
                    if (result.success) {
                        self._getNotificationSystem().showNotification('success', 'Document Deleted', 'The document has been deleted successfully.', 'check-circle');
                        self._loadDocumentsData();
                    } else {
                        self._getNotificationSystem().showNotification('error', 'Delete Failed', 'There was an error deleting the document.', 'exclamation-triangle');
                    }
                }).catch(function(error) {
                    console.error('Error deleting document:', error);
                    self._getNotificationSystem().showNotification('error', 'Delete Failed', 'There was an error deleting the document.', 'exclamation-triangle');
                });
            }
        },

        _showBulkUploadModal: function () {
            var self = this;
            var modal = $('<div class="bulk-upload-modal">' +
                '<div class="bulk-upload-content">' +
                    '<div class="bulk-upload-header">' +
                        '<h5>Bulk Upload Documents</h5>' +
                        '<button class="btn-close-modal">&times;</button>' +
                    '</div>' +
                    '<div class="bulk-upload-body">' +
                        '<div class="upload-zone" id="upload-zone">' +
                            '<i class="fa fa-cloud-upload-alt"></i>' +
                            '<h6>Drag and drop files here or click to select</h6>' +
                            '<p>Supported formats: PDF, DOC, DOCX, JPG, PNG (Max 10MB each)</p>' +
                            '<input type="file" id="bulk-file-input" multiple accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" style="display: none;">' +
                        '</div>' +
                        '<div class="upload-progress" id="upload-progress" style="display: none;">' +
                            '<h6>Upload Progress</h6>' +
                            '<div id="progress-list"></div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="comment-modal-footer">' +
                        '<button type="button" class="acmst-btn acmst-btn-secondary" id="cancel-bulk-upload">Cancel</button>' +
                        '<button type="button" class="acmst-btn acmst-btn-primary" id="start-upload" disabled>Start Upload</button>' +
                    '</div>' +
                '</div>' +
            '</div>');
            
            $('body').append(modal);
            
            // Setup drag and drop
            self._setupBulkUploadDragDrop(modal);
            
            // Handle modal events
            modal.find('.btn-close-modal, #cancel-bulk-upload').on('click', function() {
                modal.remove();
            });
            
            modal.find('#start-upload').on('click', function() {
                self._startBulkUpload(modal);
            });
            
            modal.on('click', function(e) {
                if (e.target === modal[0]) {
                    modal.remove();
                }
            });
        },

        _createFolder: function () {
            var self = this;
            var folderName = prompt('Enter folder name:');
            
            if (folderName) {
                ajax.jsonRpc('/admission/documents/create-folder', 'call', {
                    name: folderName
                }).then(function(result) {
                    if (result.success) {
                        self._getNotificationSystem().showNotification('success', 'Folder Created', 'The folder has been created successfully.', 'check-circle');
                        self._loadDocumentsData();
                    } else {
                        self._getNotificationSystem().showNotification('error', 'Create Failed', 'There was an error creating the folder.', 'exclamation-triangle');
                    }
                }).catch(function(error) {
                    console.error('Error creating folder:', error);
                    self._getNotificationSystem().showNotification('error', 'Create Failed', 'There was an error creating the folder.', 'exclamation-triangle');
                });
            }
        },

        _downloadAllDocuments: function () {
            window.open('/admission/documents/download-all', '_blank');
        }
    });

    // Analytics Dashboard Widget
    publicWidget.registry.PortalAnalytics = publicWidget.Widget.extend({
        selector: '.acmst-portal-container',
        events: {
            'click #analytics-tab': '_onAnalyticsClick',
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (self.$el.find('#analytics-tab').length) {
                    self.setupAnalyticsDashboard();
                }
            });
        },

        setupAnalyticsDashboard: function () {
            var self = this;
            
            // Load analytics data
            this._loadAnalyticsData();
            
            // Setup event handlers
            this._setupAnalyticsEventHandlers();
            
            // Initialize charts
            this._initializeCharts();
            
            // Setup real-time updates
            this._setupRealTimeUpdates();
        },

        _loadAnalyticsData: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/analytics/data', 'call')
                .then(function(result) {
                    if (result.success) {
                        self._updateMetrics(result.metrics);
                        self._updateCharts(result.charts);
                        self._updateActivityFeed(result.activities);
                        self._updateReports(result.reports);
                    }
                })
                .catch(function(error) {
                    console.error('Error loading analytics data:', error);
                });
        },

        _updateMetrics: function (metrics) {
            $('#total-applications').text(metrics.total_applications || 0);
            $('#approved-applications').text(metrics.approved_applications || 0);
            $('#pending-applications').text(metrics.pending_applications || 0);
            $('#success-rate').text((metrics.success_rate || 0) + '%');
            
            // Update change indicators
            this._updateChangeIndicator('#app-change', metrics.app_change);
            this._updateChangeIndicator('#approved-change', metrics.approved_change);
            this._updateChangeIndicator('#pending-change', metrics.pending_change);
            this._updateChangeIndicator('#success-change', metrics.success_change);
        },

        _updateChangeIndicator: function (selector, change) {
            var $indicator = $(selector);
            var $icon = $indicator.find('i');
            var $text = $indicator.find('span').last();
            
            if (change > 0) {
                $indicator.removeClass('negative neutral').addClass('positive');
                $icon.removeClass('fa-arrow-down fa-minus').addClass('fa-arrow-up');
                $text.text('+' + change + '%');
            } else if (change < 0) {
                $indicator.removeClass('positive neutral').addClass('negative');
                $icon.removeClass('fa-arrow-up fa-minus').addClass('fa-arrow-down');
                $text.text(change + '%');
            } else {
                $indicator.removeClass('positive negative').addClass('neutral');
                $icon.removeClass('fa-arrow-up fa-arrow-down').addClass('fa-minus');
                $text.text('0%');
            }
        },

        _updateCharts: function (charts) {
            this._updateTrendsChart(charts.trends);
            this._updateStatusChart(charts.status);
        },

        _updateTrendsChart: function (data) {
            var ctx = document.getElementById('application-trends-chart');
            if (!ctx) return;
            
            var chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels || [],
                    datasets: [{
                        label: 'Applications',
                        data: data.applications || [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }, {
                        label: 'Approved',
                        data: data.approved || [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        }
                    }
                }
            });
        },

        _updateStatusChart: function (data) {
            var ctx = document.getElementById('status-distribution-chart');
            if (!ctx) return;
            
            var chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels || [],
                    datasets: [{
                        data: data.values || [],
                        backgroundColor: [
                            '#3b82f6',
                            '#10b981',
                            '#f59e0b',
                            '#ef4444',
                            '#8b5cf6'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
            
            // Update legend
            this._updateStatusLegend(data.labels, data.values);
        },

        _updateStatusLegend: function (labels, values) {
            var $legend = $('#status-legend');
            $legend.empty();
            
            var colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
            
            labels.forEach(function(label, index) {
                var $item = $('<div class="legend-item">' +
                    '<div class="legend-color" style="background-color: ' + colors[index] + '"></div>' +
                    '<div class="legend-label">' + label + '</div>' +
                    '<div class="legend-value">' + (values[index] || 0) + '</div>' +
                '</div>');
                $legend.append($item);
            });
        },

        _updateActivityFeed: function (activities) {
            var $feed = $('#activity-feed');
            $feed.empty();
            
            if (activities.length === 0) {
                $feed.html('<div class="text-center text-muted py-3">No recent activity</div>');
                return;
            }
            
            activities.forEach(function(activity) {
                var $item = self._createActivityItem(activity);
                $feed.append($item);
            });
        },

        _createActivityItem: function (activity) {
            var iconClass = 'fa-' + (activity.type === 'application' ? 'file-alt' : 
                                    activity.type === 'document' ? 'file' :
                                    activity.type === 'health' ? 'heartbeat' : 'check-circle');
            
            var $item = $('<div class="activity-item">' +
                '<div class="activity-icon ' + activity.type + '">' +
                    '<i class="fa ' + iconClass + '"></i>' +
                '</div>' +
                '<div class="activity-content">' +
                    '<div class="activity-title">' + activity.title + '</div>' +
                    '<div class="activity-description">' + activity.description + '</div>' +
                    '<div class="activity-time">' + activity.time + '</div>' +
                '</div>' +
            '</div>');
            
            return $item;
        },

        _updateReports: function (reports) {
            var $grid = $('#reports-grid');
            $grid.empty();
            
            reports.forEach(function(report) {
                var $card = self._createReportCard(report);
                $grid.append($card);
            });
        },

        _createReportCard: function (report) {
            var $card = $('<div class="report-card">' +
                '<div class="report-header">' +
                    '<div class="report-title">' + report.title + '</div>' +
                    '<div class="report-icon" style="background-color: ' + report.color + '">' +
                        '<i class="fa ' + report.icon + '"></i>' +
                    '</div>' +
                '</div>' +
                '<div class="report-content">' +
                    '<div class="report-description">' + report.description + '</div>' +
                    '<div class="report-metrics">' +
                        report.metrics.map(function(metric) {
                            return '<div class="report-metric">' +
                                '<div class="report-metric-value">' + metric.value + '</div>' +
                                '<div class="report-metric-label">' + metric.label + '</div>' +
                            '</div>';
                        }).join('') +
                    '</div>' +
                '</div>' +
                '<div class="report-actions">' +
                    '<button class="btn btn-sm btn-outline-primary" data-action="view" data-report-id="' + report.id + '">View</button>' +
                    '<button class="btn btn-sm btn-outline-secondary" data-action="download" data-report-id="' + report.id + '">Download</button>' +
                '</div>' +
            '</div>');
            
            return $card;
        },

        _setupAnalyticsEventHandlers: function () {
            var self = this;
            
            // Time period change
            $('#time-period').on('change', function() {
                var period = $(this).val();
                self._loadAnalyticsData(period);
            });
            
            // Refresh button
            $('#refresh-analytics').on('click', function() {
                self._loadAnalyticsData();
            });
            
            // Chart type controls
            $('[data-chart]').on('click', function() {
                var chartType = $(this).data('chart');
                self._switchChartType(chartType);
                $('[data-chart]').removeClass('active');
                $(this).addClass('active');
            });
            
            // Report actions
            $(document).on('click', '[data-action="view"]', function(e) {
                e.preventDefault();
                var reportId = $(this).data('report-id');
                self._viewReport(reportId);
            });
            
            $(document).on('click', '[data-action="download"]', function(e) {
                e.preventDefault();
                var reportId = $(this).data('report-id');
                self._downloadReport(reportId);
            });
            
            // Generate report
            $('#generate-report').on('click', function() {
                self._generateReport();
            });
            
            // Export data
            $('#export-data').on('click', function() {
                self._exportData();
            });
        },

        _switchChartType: function (chartType) {
            // This would switch the chart type (line, bar, area)
            // Implementation depends on chart library being used
            console.log('Switching to chart type:', chartType);
        },

        _viewReport: function (reportId) {
            window.open('/admission/analytics/report/' + reportId, '_blank');
        },

        _downloadReport: function (reportId) {
            window.open('/admission/analytics/download/' + reportId, '_blank');
        },

        _generateReport: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/analytics/generate-report', 'call')
                .then(function(result) {
                    if (result.success) {
                        self._getNotificationSystem().showNotification('success', 'Report Generated', 'Your report has been generated successfully.', 'check-circle');
                        self._loadAnalyticsData();
                    } else {
                        self._getNotificationSystem().showNotification('error', 'Generation Failed', 'There was an error generating the report.', 'exclamation-triangle');
                    }
                })
                .catch(function(error) {
                    console.error('Error generating report:', error);
                    self._getNotificationSystem().showNotification('error', 'Generation Failed', 'There was an error generating the report.', 'exclamation-triangle');
                });
        },

        _exportData: function () {
            var self = this;
            
            ajax.jsonRpc('/admission/analytics/export-data', 'call')
                .then(function(result) {
                    if (result.success) {
                        window.open(result.download_url, '_blank');
                        self._getNotificationSystem().showNotification('success', 'Data Exported', 'Your data has been exported successfully.', 'check-circle');
                    } else {
                        self._getNotificationSystem().showNotification('error', 'Export Failed', 'There was an error exporting the data.', 'exclamation-triangle');
                    }
                })
                .catch(function(error) {
                    console.error('Error exporting data:', error);
                    self._getNotificationSystem().showNotification('error', 'Export Failed', 'There was an error exporting the data.', 'exclamation-triangle');
                });
        },

        _initializeCharts: function () {
            // Initialize Chart.js if not already loaded
            if (typeof Chart === 'undefined') {
                // Load Chart.js dynamically
                var script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
                script.onload = function() {
                    self._loadAnalyticsData();
                };
                document.head.appendChild(script);
            } else {
                this._loadAnalyticsData();
            }
        },

        _setupRealTimeUpdates: function () {
            var self = this;
            
            // Update analytics every 5 minutes
            setInterval(function() {
                self._loadAnalyticsData();
            }, 300000);
        }
    });

    // Initialize widgets
    publicWidget.registry.acmstPortalApplicationForm = PortalApplicationForm;
    publicWidget.registry.acmstPortalApplicationStatus = PortalApplicationStatus;
    publicWidget.registry.acmstPortalDocumentManagement = PortalDocumentManagement;
    publicWidget.registry.acmstPortalHealthCheck = PortalHealthCheck;
    publicWidget.registry.acmstNotificationSystem = NotificationSystem;
    publicWidget.registry.acmstPortalAnalytics = PortalAnalytics;

    return {
        PortalApplicationForm: PortalApplicationForm,
        PortalApplicationStatus: PortalApplicationStatus,
        PortalHealthCheck: PortalHealthCheck,
        NotificationSystem: NotificationSystem
    };
});
