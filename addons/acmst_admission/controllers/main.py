# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.web.controllers.main import ensure_db
import json
import base64
import logging

_logger = logging.getLogger(__name__)


class AdmissionPortal(CustomerPortal):
    """Portal controller for admission applications"""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        # Get user's applications count
        if request.env.user.has_group('acmst_admission.group_portal'):
            domain = [('portal_user_id', '=', request.env.user.id)]
            values['application_count'] = request.env['acmst.portal.application'].search_count(domain)
        else:
            values['application_count'] = 0
            
        return values

    @http.route(['/admission', '/admission/home'], type='http', auth="public", website=True)
    def admission_home(self, **kw):
        """Admission portal home page"""
        values = {
            'page_name': 'admission_home',
            'programs': request.env['acmst.program'].search([]),
            'batches': request.env['acmst.batch'].search([]),
        }
        return request.render('acmst_admission.portal_admission_home', values)

    @http.route('/admission/apply', type='http', auth="public", website=True)
    def admission_apply(self, **kw):
        """Application form page"""
        values = {
            'page_name': 'admission_apply',
            'programs': request.env['acmst.program'].search([]),
            'batches': request.env['acmst.batch'].search([]),
            'countries': request.env['res.country'].search([]),
        }
        return request.render('acmst_admission.portal_admission_apply', values)

    @http.route('/admission/status', type='http', auth="user", website=True)
    def admission_status(self, **kw):
        """Application status page"""
        domain = [('portal_user_id', '=', request.env.user.id)]
        applications = request.env['acmst.portal.application'].search(domain)
        
        values = {
            'page_name': 'admission_status',
            'applications': applications,
        }
        return request.render('acmst_admission.portal_admission_status', values)

    @http.route('/admission/status/<int:application_id>', type='http', auth="user", website=True)
    def admission_status_detail(self, application_id, **kw):
        """Application status detail page"""
        application = request.env['acmst.portal.application'].browse(application_id)
        
        if not application.exists() or application.portal_user_id != request.env.user:
            return request.redirect('/admission/status')
        
        values = {
            'page_name': 'admission_status_detail',
            'application': application,
        }
        return request.render('acmst_admission.portal_admission_status_detail', values)

    @http.route('/admission/health-check/<int:application_id>', type='http', auth="user", website=True)
    def admission_health_check(self, application_id, **kw):
        """Health check form page"""
        application = request.env['acmst.portal.application'].browse(application_id)
        
        if not application.exists() or application.portal_user_id != request.env.user:
            return request.redirect('/admission/status')
        
        # Check if health check is required
        if application.state not in ['approved'] or not application.admission_file_id:
            return request.redirect('/admission/status')
        
        admission_file = application.admission_file_id
        if admission_file.state != 'health_required':
            return request.redirect('/admission/status')
        
        values = {
            'page_name': 'admission_health_check',
            'application': application,
            'admission_file': admission_file,
        }
        return request.render('acmst_admission.portal_admission_health_check', values)

    @http.route('/admission/conditions/<int:application_id>', type='http', auth="user", website=True)
    def admission_conditions(self, application_id, **kw):
        """Conditions page"""
        application = request.env['acmst.portal.application'].browse(application_id)
        
        if not application.exists() or application.portal_user_id != request.env.user:
            return request.redirect('/admission/status')
        
        if not application.admission_file_id:
            return request.redirect('/admission/status')
        
        admission_file = application.admission_file_id
        conditions = admission_file.coordinator_conditions_ids
        
        values = {
            'page_name': 'admission_conditions',
            'application': application,
            'admission_file': admission_file,
            'conditions': conditions,
        }
        return request.render('acmst_admission.portal_admission_conditions', values)

    @http.route('/admission/submit', type='http', methods=['POST'], auth="public", website=True, csrf=False)
    def admission_submit(self, **kw):
        """Submit application form"""
        try:
            # Get form data
            form_data = self._prepare_application_data(kw)
            
            # Validate required fields
            errors = self._validate_application_data(form_data)
            if errors:
                return json.dumps({
                    'success': False,
                    'error': 'Validation errors: ' + ', '.join(errors)
                })
            
            # Create application
            application = request.env['acmst.portal.application'].create(form_data)
            
            # Submit application
            application.action_submit()
            
            return json.dumps({
                'success': True,
                'application_id': application.id,
                'message': 'Application submitted successfully!'
            })
            
        except Exception as e:
            _logger.error('Error submitting application: %s', str(e))
            return json.dumps({
                'success': False,
                'error': 'An error occurred while submitting your application. Please try again.'
            })

    @http.route('/admission/save-draft', type='http', methods=['POST'], auth="public", website=True, csrf=False)
    def admission_save_draft(self, **kw):
        """Save application as draft"""
        try:
            # Get form data
            form_data = self._prepare_application_data(kw)
            
            # Create or update draft
            if 'application_id' in kw and kw['application_id']:
                application = request.env['acmst.portal.application'].browse(int(kw['application_id']))
                if application.exists() and application.portal_user_id == request.env.user:
                    application.write(form_data)
                else:
                    return json.dumps({'success': False, 'error': 'Invalid application'})
            else:
                application = request.env['acmst.portal.application'].create(form_data)
            
            return json.dumps({
                'success': True,
                'application_id': application.id,
                'message': 'Draft saved successfully!'
            })
            
        except Exception as e:
            _logger.error('Error saving draft: %s', str(e))
            return json.dumps({
                'success': False,
                'error': 'An error occurred while saving your draft. Please try again.'
            })

    @http.route('/admission/health-check/submit', type='http', methods=['POST'], auth="user", website=True, csrf=False)
    def health_check_submit(self, **kw):
        """Submit health check form"""
        try:
            application_id = int(kw.get('application_id', 0))
            application = request.env['acmst.portal.application'].browse(application_id)
            
            if not application.exists() or application.portal_user_id != request.env.user:
                return json.dumps({'success': False, 'error': 'Invalid application'})
            
            if not application.admission_file_id:
                return json.dumps({'success': False, 'error': 'No admission file found'})
            
            admission_file = application.admission_file_id
            if admission_file.state != 'health_required':
                return json.dumps({'success': False, 'error': 'Health check not required'})
            
            # Prepare health check data
            health_data = self._prepare_health_check_data(kw)
            
            # Create health check
            health_check = request.env['acmst.health.check'].create(health_data)
            
            # Submit health check
            health_check.action_submit()
            
            return json.dumps({
                'success': True,
                'message': 'Health check submitted successfully!'
            })
            
        except Exception as e:
            _logger.error('Error submitting health check: %s', str(e))
            return json.dumps({
                'success': False,
                'error': 'An error occurred while submitting your health check. Please try again.'
            })

    @http.route('/admission/condition/complete', type='http', methods=['POST'], auth="user", website=True, csrf=False)
    def condition_complete(self, **kw):
        """Mark condition as complete"""
        try:
            condition_id = int(kw.get('condition_id', 0))
            condition = request.env['acmst.coordinator.condition'].browse(condition_id)
            
            if not condition.exists():
                return json.dumps({'success': False, 'error': 'Invalid condition'})
            
            # Check if user has access to this condition
            if condition.admission_file_id.portal_user_id != request.env.user:
                return json.dumps({'success': False, 'error': 'Access denied'})
            
            # Mark as complete
            condition.action_complete()
            
            return json.dumps({
                'success': True,
                'message': 'Condition marked as complete!'
            })
            
        except Exception as e:
            _logger.error('Error completing condition: %s', str(e))
            return json.dumps({
                'success': False,
                'error': 'An error occurred while completing the condition. Please try again.'
            })

    def _prepare_application_data(self, kw):
        """Prepare application data from form"""
        data = {
            'applicant_name': kw.get('applicant_name', '').strip(),
            'national_id': kw.get('national_id', '').strip(),
            'phone': kw.get('phone', '').strip(),
            'email': kw.get('email', '').strip(),
            'program_id': int(kw.get('program_id', 0)) if kw.get('program_id') else False,
            'batch_id': int(kw.get('batch_id', 0)) if kw.get('batch_id') else False,
            'birth_date': kw.get('birth_date', ''),
            'gender': kw.get('gender', ''),
            'nationality': kw.get('nationality', '').strip(),
            'address': kw.get('address', '').strip(),
            'emergency_contact': kw.get('emergency_contact', '').strip(),
            'emergency_phone': kw.get('emergency_phone', '').strip(),
            'previous_education': kw.get('previous_education', '').strip(),
            'portal_user_id': request.env.user.id if request.env.user != request.env.ref('base.public_user') else False,
            'ip_address': request.httprequest.environ.get('REMOTE_ADDR', ''),
            'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', ''),
        }
        
        # Handle file upload
        if 'documents' in request.httprequest.files:
            file = request.httprequest.files['documents']
            if file and file.filename:
                data['documents'] = base64.b64encode(file.read())
                data['documents_filename'] = file.filename
        
        return data

    def _prepare_health_check_data(self, kw):
        """Prepare health check data from form"""
        application_id = int(kw.get('application_id', 0))
        application = request.env['acmst.portal.application'].browse(application_id)
        
        data = {
            'admission_file_id': application.admission_file_id.id,
            'check_date': fields.Datetime.now(),
            'examiner_id': request.env.user.id,
            'has_chronic_diseases': kw.get('has_chronic_diseases') == 'on',
            'chronic_diseases_details': kw.get('chronic_diseases_details', '').strip(),
            'takes_medications': kw.get('takes_medications') == 'on',
            'medications_details': kw.get('medications_details', '').strip(),
            'has_allergies': kw.get('has_allergies') == 'on',
            'allergies_details': kw.get('allergies_details', '').strip(),
            'has_disabilities': kw.get('has_disabilities') == 'on',
            'disabilities_details': kw.get('disabilities_details', '').strip(),
            'blood_type': kw.get('blood_type', ''),
            'height': float(kw.get('height', 0)) if kw.get('height') else 0,
            'weight': float(kw.get('weight', 0)) if kw.get('weight') else 0,
            'medical_fitness': kw.get('medical_fitness', ''),
            'medical_notes': kw.get('medical_notes', '').strip(),
            'restrictions': kw.get('restrictions', '').strip(),
            'follow_up_required': kw.get('follow_up_required') == 'on',
            'follow_up_date': kw.get('follow_up_date', ''),
        }
        
        # Handle file uploads
        for field_name in ['medical_reports', 'lab_results', 'other_documents']:
            if field_name in request.httprequest.files:
                file = request.httprequest.files[field_name]
                if file and file.filename:
                    data[field_name] = base64.b64encode(file.read())
                    data[field_name + '_filename'] = file.filename
        
        return data

    def _validate_application_data(self, data):
        """Validate application data"""
        errors = []
        
        # Required fields
        required_fields = [
            'applicant_name', 'national_id', 'phone', 'email',
            'program_id', 'batch_id', 'birth_date', 'gender',
            'nationality', 'address', 'emergency_contact', 'emergency_phone'
        ]
        
        for field in required_fields:
            if not data.get(field):
                errors.append(field.replace('_', ' ').title() + ' is required')
        
        # Email validation
        if data.get('email') and '@' not in data['email']:
            errors.append('Please enter a valid email address')
        
        # National ID validation
        if data.get('national_id') and (not data['national_id'].isdigit() or len(data['national_id']) != 10):
            errors.append('National ID must be exactly 10 digits')
        
        # Phone validation
        if data.get('phone') and not data['phone'].replace('+', '').replace('-', '').replace(' ', '').isdigit():
            errors.append('Please enter a valid phone number')
        
        return errors
