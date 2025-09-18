/* ACMST Core Settings JavaScript */

odoo.define('acmst_core_settings.acmst_core_settings', [
    'web.core',
    'web.FormView',
    'web.ListView',
    'web.KanbanView',
    'web.Dialog'
], function (require) {
    'use strict';

    var core = require('web.core');
    var FormView = require('web.FormView');
    var ListView = require('web.ListView');
    var KanbanView = require('web.KanbanView');
    var Dialog = require('web.Dialog');

    var _t = core._t;

    // Form View Enhancements
    FormView.include({
        start: function () {
            this._super.apply(this, arguments);
            this._enhanceFormView();
        },

        _enhanceFormView: function () {
            var self = this;
            
            // Add custom event listeners
            this.$el.on('click', '.oe_stat_button', function (e) {
                e.preventDefault();
                var $button = $(this);
                var action = $button.data('action');
                if (action) {
                    self.do_action(action);
                }
            });

            // Add progress bar animations
            this.$('.o_progressbar').each(function () {
                var $progress = $(this);
                var percentage = $progress.data('percentage') || 0;
                setTimeout(function () {
                    $progress.find('.o_progressbar_fill').css('width', percentage + '%');
                }, 100);
            });
        }
    });

    // List View Enhancements
    ListView.include({
        start: function () {
            this._super.apply(this, arguments);
            this._enhanceListView();
        },

        _enhanceListView: function () {
            var self = this;
            
            // Add custom sorting indicators
            this.$('.o_column_sortable').on('click', function () {
                var $header = $(this);
                $header.toggleClass('o_sort_up o_sort_down');
            });

            // Add row highlighting
            this.$('.o_data_row').hover(
                function () {
                    $(this).addClass('o_row_highlighted');
                },
                function () {
                    $(this).removeClass('o_row_highlighted');
                }
            );
        }
    });

    // Kanban View Enhancements
    KanbanView.include({
        start: function () {
            this._super.apply(this, arguments);
            this._enhanceKanbanView();
        },

        _enhanceKanbanView: function () {
            var self = this;
            
            // Add card animations
            this.$('.oe_kanban_card').each(function (index) {
                var $card = $(this);
                setTimeout(function () {
                    $card.addClass('o_kanban_card_animated');
                }, index * 100);
            });

            // Add hover effects
            this.$('.oe_kanban_card').hover(
                function () {
                    $(this).addClass('o_kanban_card_hover');
                },
                function () {
                    $(this).removeClass('o_kanban_card_hover');
                }
            );
        }
    });

    // Custom Widget for Statistics
    var AcmstStatisticsWidget = core.Class.extend({
        init: function (parent, options) {
            this.parent = parent;
            this.options = options || {};
        },

        start: function () {
            this._render();
        },

        _render: function () {
            var self = this;
            var $container = this.parent.$('.oe_stat_button');
            
            $container.each(function () {
                var $button = $(this);
                var value = $button.find('.o_stat_info').text();
                var number = parseInt(value) || 0;
                
                // Add animation for numbers
                if (number > 0) {
                    self._animateNumber($button.find('.o_stat_info'), number);
                }
            });
        },

        _animateNumber: function ($element, target) {
            var current = 0;
            var increment = Math.ceil(target / 20);
            var timer = setInterval(function () {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                $element.text(current);
            }, 50);
        }
    });

    // Custom Dialog for Batch Creation
    var AcmstBatchCreationDialog = Dialog.extend({
        init: function (parent, options) {
            this._super(parent, _.extend({
                title: _t('Create Multiple Batches'),
                size: 'large',
                buttons: [
                    {
                        text: _t('Preview'),
                        classes: 'btn-info',
                        click: this._onPreview.bind(this)
                    },
                    {
                        text: _t('Create'),
                        classes: 'btn-primary',
                        click: this._onCreate.bind(this)
                    },
                    {
                        text: _t('Cancel'),
                        classes: 'btn-secondary',
                        click: this._onCancel.bind(this)
                    }
                ]
            }, options));
        },

        _onPreview: function () {
            // Implement preview functionality
            this.trigger('preview');
        },

        _onCreate: function () {
            // Implement create functionality
            this.trigger('create');
        },

        _onCancel: function () {
            this.close();
        }
    });

    // Utility Functions
    var AcmstUtils = {
        formatDate: function (date) {
            if (!date) return '';
            var d = new Date(date);
            return d.toLocaleDateString();
        },

        formatNumber: function (number) {
            if (!number) return '0';
            return number.toLocaleString();
        },

        showNotification: function (title, message, type) {
            type = type || 'info';
            var notification = new Dialog(this, {
                title: title,
                size: 'medium',
                $content: $('<div>').text(message),
                buttons: [{
                    text: _t('OK'),
                    classes: 'btn-primary',
                    click: function () {
                        notification.close();
                    }
                }]
            });
            notification.open();
        },

        validateForm: function ($form) {
            var isValid = true;
            var errors = [];

            $form.find('input[required], select[required], textarea[required]').each(function () {
                var $field = $(this);
                if (!$field.val()) {
                    isValid = false;
                    errors.push($field.attr('name') + ' is required');
                    $field.addClass('o_field_error');
                } else {
                    $field.removeClass('o_field_error');
                }
            });

            if (!isValid) {
                this.showNotification('Validation Error', errors.join('<br>'), 'danger');
            }

            return isValid;
        }
    };

    // Export utilities
    return {
        AcmstStatisticsWidget: AcmstStatisticsWidget,
        AcmstBatchCreationDialog: AcmstBatchCreationDialog,
        AcmstUtils: AcmstUtils
    };
});
