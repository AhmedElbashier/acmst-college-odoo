/* ACMST Admission Module - Backend JavaScript */

odoo.define('acmst_admission.admission', ['web.FormController', 'web.ListController', 'web.Dialog', 'web.core'], function (FormController, ListController, Dialog, core) {
    'use strict';

    var _t = core._t;

    // Form Controller Enhancements
    FormController.include({
        _onButtonClicked: function (event) {
            var self = this;
            var $target = $(event.currentTarget);
            var data = $target.data();
            
            // Handle admission file actions
            if (this.modelName === 'acmst.admission.file') {
                if (data.name === 'action_submit_ministry') {
                    event.preventDefault();
                    this._confirmAction('Submit to Ministry', 'Are you sure you want to submit this application to the ministry for approval?', function() {
                        self.trigger_up('execute_action', {
                            action_data: {
                                type: 'ir.actions.server',
                                res_model: 'acmst.admission.file',
                                res_id: self.model.get(self.handle).get('id'),
                                method: 'action_submit_ministry',
                            }
                        });
                    });
                    return;
                }
                
                if (data.name === 'action_ministry_approve') {
                    event.preventDefault();
                    this._showApprovalDialog('Ministry Approval', 'ministry_approve');
                    return;
                }
                
                if (data.name === 'action_ministry_reject') {
                    event.preventDefault();
                    this._showApprovalDialog('Ministry Rejection', 'ministry_reject');
                    return;
                }
                
                if (data.name === 'action_health_approve') {
                    event.preventDefault();
                    this._showApprovalDialog('Health Approval', 'health_approve');
                    return;
                }
                
                if (data.name === 'action_health_reject') {
                    event.preventDefault();
                    this._showApprovalDialog('Health Rejection', 'health_reject');
                    return;
                }
                
                if (data.name === 'action_coordinator_approve') {
                    event.preventDefault();
                    this._showApprovalDialog('Coordinator Approval', 'coordinator_approve');
                    return;
                }
                
                if (data.name === 'action_coordinator_reject') {
                    event.preventDefault();
                    this._showApprovalDialog('Coordinator Rejection', 'coordinator_reject');
                    return;
                }
                
                if (data.name === 'action_coordinator_conditional') {
                    event.preventDefault();
                    this._showConditionalDialog();
                    return;
                }
                
                if (data.name === 'action_manager_approve') {
                    event.preventDefault();
                    this._showApprovalDialog('Manager Approval', 'manager_approve');
                    return;
                }
                
                if (data.name === 'action_manager_reject') {
                    event.preventDefault();
                    this._showApprovalDialog('Manager Rejection', 'manager_reject');
                    return;
                }
                
                if (data.name === 'action_complete') {
                    event.preventDefault();
                    this._confirmAction('Complete Admission', 'Are you sure you want to complete this admission process? This will create a student record.', function() {
                        self.trigger_up('execute_action', {
                            action_data: {
                                type: 'ir.actions.server',
                                res_model: 'acmst.admission.file',
                                res_id: self.model.get(self.handle).get('id'),
                                method: 'action_complete',
                            }
                        });
                    });
                    return;
                }
                
                if (data.name === 'action_cancel') {
                    event.preventDefault();
                    this._confirmAction('Cancel Admission', 'Are you sure you want to cancel this admission file?', function() {
                        self.trigger_up('execute_action', {
                            action_data: {
                                type: 'ir.actions.server',
                                res_model: 'acmst.admission.file',
                                res_id: self.model.get(self.handle).get('id'),
                                method: 'action_cancel',
                            }
                        });
                    });
                    return;
                }
            }
            
            return this._super.apply(this, arguments);
        },
        
        _confirmAction: function(title, message, callback) {
            var dialog = new Dialog(this, {
                title: title,
                size: 'medium',
                $content: $('<div>').html(message),
                buttons: [
                    {
                        text: _t('Cancel'),
                        close: true,
                        classes: 'btn-secondary'
                    },
                    {
                        text: _t('Confirm'),
                        classes: 'btn-primary',
                        click: function() {
                            callback();
                            dialog.close();
                        }
                    }
                ]
            });
            dialog.open();
        },
        
        _showApprovalDialog: function(title, actionType) {
            var self = this;
            var $content = $('<div>').html(
                '<div class="form-group">' +
                '<label for="approval-comments">Comments (Optional)</label>' +
                '<textarea id="approval-comments" class="form-control" rows="3" placeholder="Enter comments about this approval..."></textarea>' +
                '</div>' +
                '<div class="form-check">' +
                '<input type="checkbox" class="form-check-input" id="send-notification" checked>' +
                '<label class="form-check-label" for="send-notification">Send email notification to applicant</label>' +
                '</div>'
            );
            
            var dialog = new Dialog(this, {
                title: title,
                size: 'medium',
                $content: $content,
                buttons: [
                    {
                        text: _t('Cancel'),
                        close: true,
                        classes: 'btn-secondary'
                    },
                    {
                        text: _t('Confirm'),
                        classes: 'btn-primary',
                        click: function() {
                            var comments = $('#approval-comments').val();
                            var sendNotification = $('#send-notification').is(':checked');
                            
                            self.trigger_up('execute_action', {
                                action_data: {
                                    type: 'ir.actions.server',
                                    res_model: 'acmst.admission.file',
                                    res_id: self.model.get(self.handle).get('id'),
                                    method: actionType,
                                    context: {
                                        comments: comments,
                                        send_notification: sendNotification
                                    }
                                }
                            });
                            dialog.close();
                        }
                    }
                ]
            });
            dialog.open();
        },
        
        _showConditionalDialog: function() {
            var self = this;
            var $content = $('<div>').html(
                '<div class="form-group">' +
                '<label for="condition-subject">Subject Name</label>' +
                '<input type="text" id="condition-subject" class="form-control" required>' +
                '</div>' +
                '<div class="form-group">' +
                '<label for="condition-code">Subject Code</label>' +
                '<input type="text" id="condition-code" class="form-control">' +
                '</div>' +
                '<div class="form-group">' +
                '<label for="condition-level">Level</label>' +
                '<select id="condition-level" class="form-control" required>' +
                '<option value="">Select Level</option>' +
                '<option value="level2">Level 2</option>' +
                '<option value="level3">Level 3</option>' +
                '</select>' +
                '</div>' +
                '<div class="form-group">' +
                '<label for="condition-description">Description</label>' +
                '<textarea id="condition-description" class="form-control" rows="3" required placeholder="Describe the condition..."></textarea>' +
                '</div>' +
                '<div class="form-group">' +
                '<label for="condition-deadline">Deadline</label>' +
                '<input type="date" id="condition-deadline" class="form-control">' +
                '</div>' +
                '<div class="form-group">' +
                '<label for="approval-comments">Comments (Optional)</label>' +
                '<textarea id="approval-comments" class="form-control" rows="3" placeholder="Enter comments about this conditional approval..."></textarea>' +
                '</div>'
            );
            
            // Set default deadline to 30 days from now
            var defaultDeadline = new Date();
            defaultDeadline.setDate(defaultDeadline.getDate() + 30);
            $('#condition-deadline').val(defaultDeadline.toISOString().split('T')[0]);
            
            var dialog = new Dialog(this, {
                title: 'Conditional Approval',
                size: 'large',
                $content: $content,
                buttons: [
                    {
                        text: _t('Cancel'),
                        close: true,
                        classes: 'btn-secondary'
                    },
                    {
                        text: _t('Confirm'),
                        classes: 'btn-primary',
                        click: function() {
                            var subjectName = $('#condition-subject').val();
                            var subjectCode = $('#condition-code').val();
                            var level = $('#condition-level').val();
                            var description = $('#condition-description').val();
                            var deadline = $('#condition-deadline').val();
                            var comments = $('#approval-comments').val();
                            
                            if (!subjectName || !level || !description || !deadline) {
                                alert('Please fill in all required fields.');
                                return;
                            }
                            
                            self.trigger_up('execute_action', {
                                action_data: {
                                    type: 'ir.actions.server',
                                    res_model: 'acmst.admission.file',
                                    res_id: self.model.get(self.handle).get('id'),
                                    method: 'action_coordinator_conditional',
                                    context: {
                                        condition_data: {
                                            subject_name: subjectName,
                                            subject_code: subjectCode,
                                            level: level,
                                            description: description,
                                            deadline: deadline
                                        },
                                        comments: comments
                                    }
                                }
                            });
                            dialog.close();
                        }
                    }
                ]
            });
            dialog.open();
        }
    });

    // List Controller Enhancements
    ListController.include({
        _onButtonClicked: function (event) {
            var self = this;
            var $target = $(event.currentTarget);
            var data = $target.data();
            
            // Handle bulk actions
            if (data.name === 'action_bulk_approve') {
                event.preventDefault();
                this._showBulkActionDialog('Bulk Approval', 'approve');
                return;
            }
            
            if (data.name === 'action_bulk_reject') {
                event.preventDefault();
                this._showBulkActionDialog('Bulk Rejection', 'reject');
                return;
            }
            
            return this._super.apply(this, arguments);
        },
        
        _showBulkActionDialog: function(title, action) {
            var self = this;
            var selectedRecords = this.getSelectedRecords();
            
            if (selectedRecords.length === 0) {
                alert('Please select at least one record.');
                return;
            }
            
            var $content = $('<div>').html(
                '<p>You are about to ' + action + ' ' + selectedRecords.length + ' record(s).</p>' +
                '<div class="form-group">' +
                '<label for="bulk-comments">Comments (Optional)</label>' +
                '<textarea id="bulk-comments" class="form-control" rows="3" placeholder="Enter comments about this bulk action..."></textarea>' +
                '</div>' +
                '<div class="form-check">' +
                '<input type="checkbox" class="form-check-input" id="bulk-send-notification" checked>' +
                '<label class="form-check-label" for="bulk-send-notification">Send email notifications</label>' +
                '</div>'
            );
            
            var dialog = new Dialog(this, {
                title: title,
                size: 'medium',
                $content: $content,
                buttons: [
                    {
                        text: _t('Cancel'),
                        close: true,
                        classes: 'btn-secondary'
                    },
                    {
                        text: _t('Confirm'),
                        classes: 'btn-primary',
                        click: function() {
                            var comments = $('#bulk-comments').val();
                            var sendNotification = $('#bulk-send-notification').is(':checked');
                            
                            // Execute bulk action
                            self._executeBulkAction(action, comments, sendNotification);
                            dialog.close();
                        }
                    }
                ]
            });
            dialog.open();
        },
        
        _executeBulkAction: function(action, comments, sendNotification) {
            var self = this;
            var selectedRecords = this.getSelectedRecords();
            var promises = [];
            
            selectedRecords.forEach(function(record) {
                var promise = self._rpc({
                    model: record.model,
                    method: 'action_' + action,
                    args: [record.res_id],
                    context: {
                        comments: comments,
                        send_notification: sendNotification
                    }
                });
                promises.push(promise);
            });
            
            Promise.all(promises).then(function() {
                self.reload();
                self.displayNotification({
                    title: 'Success',
                    message: 'Bulk action completed successfully.',
                    type: 'success'
                });
            }).catch(function(error) {
                self.displayNotification({
                    title: 'Error',
                    message: 'An error occurred while executing the bulk action.',
                    type: 'danger'
                });
            });
        }
    });

    // Status Bar Enhancements
    $('.o_statusbar_status').each(function() {
        var $statusbar = $(this);
        var $buttons = $statusbar.find('.o_statusbar_status_button');
        
        $buttons.each(function(index) {
            var $button = $(this);
            var status = $button.data('status') || $button.attr('class').match(/o_statusbar_status_(\w+)/);
            
            if (status) {
                status = status[1] || status;
                $button.addClass('o_statusbar_status_' + status);
            }
        });
    });

    // Form Validation Enhancements
    $('.o_form_view').on('change', 'input[required], select[required], textarea[required]', function() {
        var $field = $(this);
        var value = $field.val();
        
        if (value && value.trim() !== '') {
            $field.removeClass('is-invalid').addClass('is-valid');
        } else {
            $field.removeClass('is-valid').addClass('is-invalid');
        }
    });

    // Auto-save functionality
    var autoSaveTimer;
    $('.o_form_view').on('input', 'input, select, textarea', function() {
        var $field = $(this);
        var $form = $field.closest('form');
        
        clearTimeout(autoSaveTimer);
        autoSaveTimer = setTimeout(function() {
            if ($form.length && $form.data('model') === 'acmst.admission.file') {
                // Auto-save logic would go here
                console.log('Auto-saving form...');
            }
        }, 2000);
    });

    // File Upload Enhancements
    $('.o_field_binary').each(function() {
        var $field = $(this);
        var $input = $field.find('input[type="file"]');
        var $label = $field.find('label');
        
        if ($input.length && $label.length) {
            $label.on('click', function() {
                $input.click();
            });
            
            $input.on('change', function() {
                var fileName = this.files[0] ? this.files[0].name : 'No file selected';
                $label.text(fileName);
            });
        }
    });

    // Search Enhancements
    $('.o_searchview').on('keyup', 'input', function() {
        var $input = $(this);
        var query = $input.val();
        
        if (query.length >= 3) {
            // Auto-suggest functionality would go here
            console.log('Searching for:', query);
        }
    });

    // Responsive Enhancements
    $(window).on('resize', function() {
        var windowWidth = $(window).width();
        
        if (windowWidth < 768) {
            $('.o_statusbar_status .o_statusbar_status_button').addClass('btn-sm');
        } else {
            $('.o_statusbar_status .o_statusbar_status_button').removeClass('btn-sm');
        }
    });

    // Initialize on page load
    $(document).ready(function() {
        // Add loading states to buttons
        $('.o_form_view button[type="button"]').on('click', function() {
            var $button = $(this);
            var originalText = $button.text();
            
            $button.prop('disabled', true)
                   .html('<span class="acmst-spinner"></span> ' + originalText);
            
            setTimeout(function() {
                $button.prop('disabled', false).text(originalText);
            }, 2000);
        });
        
        // Add tooltips
        $('[data-toggle="tooltip"]').tooltip();
        
        // Add confirmation dialogs to destructive actions
        $('.btn-danger').on('click', function(e) {
            if (!confirm('Are you sure you want to perform this action?')) {
                e.preventDefault();
            }
        });
    });

    return {
        FormController: FormController,
        ListController: ListController
    };
});
