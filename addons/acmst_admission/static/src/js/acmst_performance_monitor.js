/* Performance Monitoring JavaScript */
odoo.define('acmst_admission.performance_monitor', ['web.core', 'web.ajax', 'web.rpc'], function (core, ajax, rpc) {
    'use strict';

    var _t = core._t;

    var PerformanceMonitor = core.Class.extend({
        init: function (parent, options) {
            this.parent = parent;
            this.options = options || {};
            this.metrics = {};
            this.alerts = [];
            this.refreshInterval = null;
        },

        start: function () {
            this._loadInitialData();
            this._startAutoRefresh();
            this._bindEvents();
        },

        _loadInitialData: function () {
            var self = this;
            rpc.query({
                model: 'acmst.performance',
                method: 'get_performance_metrics',
                args: []
            }).then(function (data) {
                self.metrics = data;
                self._updateDashboard();
            }).catch(function (error) {
                console.error('Error loading performance metrics:', error);
            });
        },

        _startAutoRefresh: function () {
            var self = this;
            this.refreshInterval = setInterval(function () {
                self._refreshMetrics();
            }, 30000); // Refresh every 30 seconds
        },

        _refreshMetrics: function () {
            var self = this;
            rpc.query({
                model: 'acmst.performance',
                method: 'get_live_metrics',
                args: []
            }).then(function (data) {
                self.metrics = data;
                self._updateDashboard();
            }).catch(function (error) {
                console.error('Error refreshing metrics:', error);
            });
        },

        _updateDashboard: function () {
            this._updateMetricCards();
            this._updateOptimizationList();
            this._updateAlerts();
        },

        _updateMetricCards: function () {
            var metrics = this.metrics;
            
            // Update query performance
            if (metrics.query_performance) {
                this._updateMetricValue('.o_acmst_metric_card:nth-child(1) .o_acmst_metric_value', 
                    metrics.query_performance.average_time + 's');
            }
            
            // Update database load
            if (metrics.database_load) {
                this._updateMetricValue('.o_acmst_metric_card:nth-child(2) .o_acmst_metric_value', 
                    metrics.database_load.cpu_usage + '%');
            }
            
            // Update memory usage
            if (metrics.memory_usage) {
                this._updateMetricValue('.o_acmst_metric_card:nth-child(3) .o_acmst_metric_value', 
                    metrics.memory_usage.ram_consumption);
            }
            
            // Update active users
            if (metrics.active_users) {
                this._updateMetricValue('.o_acmst_metric_card:nth-child(4) .o_acmst_metric_value', 
                    metrics.active_users.count);
            }
        },

        _updateMetricValue: function (selector, value) {
            var element = document.querySelector(selector);
            if (element) {
                element.textContent = value;
            }
        },

        _updateOptimizationList: function () {
            var optimizations = this.metrics.optimizations || [];
            var container = document.querySelector('.o_acmst_optimization_list');
            
            if (container && optimizations.length > 0) {
                container.innerHTML = '';
                optimizations.forEach(function (opt) {
                    var item = document.createElement('div');
                    item.className = 'o_acmst_optimization_item';
                    item.innerHTML = 
                        '<div class="o_acmst_optimization_name">' + opt.name + '</div>' +
                        '<div class="o_acmst_optimization_status ' + (opt.active ? 'active' : 'inactive') + '">' + 
                            (opt.active ? 'Active' : 'Inactive') + '</div>' +
                        '<div class="o_acmst_optimization_gain">+' + opt.performance_gain + '%</div>';
                    container.appendChild(item);
                });
            }
        },

        _updateAlerts: function () {
            var alerts = this.metrics.alerts || [];
            var container = document.querySelector('.o_acmst_alerts_list');
            
            if (container && alerts.length > 0) {
                container.innerHTML = '';
                alerts.forEach(function (alert) {
                    var item = document.createElement('div');
                    item.className = 'o_acmst_alert_item ' + alert.type;
                    item.innerHTML = 
                        '<i class="fa fa-' + alert.icon + '" aria-hidden="true"></i>' +
                        '<span>' + alert.message + '</span>';
                    container.appendChild(item);
                });
            }
        },

        _bindEvents: function () {
            var self = this;
            
            // Refresh button
            var refreshBtn = document.querySelector('.o_acmst_performance_actions .btn-primary');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', function () {
                    self._refreshMetrics();
                });
            }
            
            // Optimization check button
            var checkBtn = document.querySelector('.o_acmst_performance_actions .btn-secondary');
            if (checkBtn) {
                checkBtn.addEventListener('click', function () {
                    self._runOptimizationCheck();
                });
            }
            
            // Export report button
            var exportBtn = document.querySelector('.o_acmst_performance_actions .btn-info');
            if (exportBtn) {
                exportBtn.addEventListener('click', function () {
                    self._exportReport();
                });
            }
        },

        _runOptimizationCheck: function () {
            var self = this;
            rpc.query({
                model: 'acmst.performance',
                method: 'run_optimization_check',
                args: []
            }).then(function (result) {
                if (result.success) {
                    self._showNotification('Optimization check completed successfully', 'success');
                    self._refreshMetrics();
                } else {
                    self._showNotification('Optimization check failed: ' + result.message, 'error');
                }
            }).catch(function (error) {
                console.error('Error running optimization check:', error);
                self._showNotification('Error running optimization check', 'error');
            });
        },

        _exportReport: function () {
            var self = this;
            rpc.query({
                model: 'acmst.performance',
                method: 'export_performance_report',
                args: []
            }).then(function (result) {
                if (result.url) {
                    window.open(result.url, '_blank');
                } else {
                    self._showNotification('Report export failed', 'error');
                }
            }).catch(function (error) {
                console.error('Error exporting report:', error);
                self._showNotification('Error exporting report', 'error');
            });
        },

        _showNotification: function (message, type) {
            // Simple notification implementation
            var notification = document.createElement('div');
            notification.className = 'o_acmst_notification o_acmst_notification_' + type;
            notification.textContent = message;
            notification.style.cssText = 
                'position: fixed; top: 20px; right: 20px; padding: 15px 20px; ' +
                'border-radius: 4px; color: white; z-index: 9999; ' +
                'background: ' + (type === 'success' ? '#28a745' : '#dc3545') + ';';
            
            document.body.appendChild(notification);
            
            setTimeout(function () {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 3000);
        },

        destroy: function () {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
        }
    });

    return PerformanceMonitor;
});
