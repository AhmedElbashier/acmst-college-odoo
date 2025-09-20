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
            
            // National ID validation
            this.$('input[name="national_id"]').on('input', function() {
                var value = $(this).val();
                if (value.length === 10 && !/^\d{10}$/.test(value)) {
                    self._showFieldError($(this), 'National ID must be exactly 10 digits');
                } else {
                    self._clearFieldError($(this));
                }
            });
            
            // Email validation
            this.$('input[name="email"]').on('blur', function() {
                var value = $(this).val();
                if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                    self._showFieldError($(this), 'Please enter a valid email address');
                } else {
                    self._clearFieldError($(this));
                }
            });
            
            // Phone validation
            this.$('input[name="phone"]').on('blur', function() {
                var value = $(this).val();
                if (value && !/^[\+]?[0-9\s\-\(\)]{10,}$/.test(value)) {
                    self._showFieldError($(this), 'Please enter a valid phone number');
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
                $fileUpload.on('click', function() {
                    $fileInput.click();
                });
                
                $fileInput.on('change', function() {
                    var files = this.files;
                    if (files.length > 0) {
                        self._updateFileUploadDisplay(files[0]);
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

        _onFormSubmit: function (event) {
            event.preventDefault();
            var self = this;
            
            if (this._validateForm()) {
                this._submitForm();
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

        _handleFileUpload: function (file) {
            // Validate file type and size
            var allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            var maxSize = 10 * 1024 * 1024; // 10MB
            
            if (!allowedTypes.includes(file.type)) {
                this._showAlert('Please upload a valid file type (PDF, DOC, DOCX, JPG, PNG)', 'danger');
                return;
            }
            
            if (file.size > maxSize) {
                this._showAlert('File size must be less than 10MB', 'danger');
                return;
            }
            
            this._updateFileUploadDisplay(file);
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

    // Initialize widgets
    publicWidget.registry.acmstPortalApplicationForm = PortalApplicationForm;
    publicWidget.registry.acmstPortalApplicationStatus = PortalApplicationStatus;
    publicWidget.registry.acmstPortalHealthCheck = PortalHealthCheck;

    return {
        PortalApplicationForm: PortalApplicationForm,
        PortalApplicationStatus: PortalApplicationStatus,
        PortalHealthCheck: PortalHealthCheck
    };
});
