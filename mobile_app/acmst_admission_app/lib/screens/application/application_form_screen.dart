import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:acmst_admission_app/services/application_service.dart';
import 'package:acmst_admission_app/widgets/step_indicator.dart';
import 'package:acmst_admission_app/widgets/form_step.dart';
import 'package:acmst_admission_app/models/application_model.dart';

class ApplicationFormScreen extends StatefulWidget {
  const ApplicationFormScreen({Key? key}) : super(key: key);

  @override
  State<ApplicationFormScreen> createState() => _ApplicationFormScreenState();
}

class _ApplicationFormScreenState extends State<ApplicationFormScreen> {
  final PageController _pageController = PageController();
  int _currentStep = 0;
  final int _totalSteps = 4;
  
  final ApplicationModel _application = ApplicationModel();
  bool _isLoading = false;
  bool _isDraftSaving = false;

  final List<String> _stepTitles = [
    'Personal Information',
    'Admission Details',
    'Documents',
    'Review & Submit'
  ];

  @override
  void initState() {
    super.initState();
    _loadDraft();
  }

  Future<void> _loadDraft() async {
    final applicationService = Provider.of<ApplicationService>(context, listen: false);
    final draft = await applicationService.getDraft();
    if (draft != null) {
      setState(() {
        _application.copyFrom(draft);
        _currentStep = draft.currentStep ?? 0;
      });
    }
  }

  Future<void> _saveDraft() async {
    if (_isDraftSaving) return;
    
    setState(() {
      _isDraftSaving = true;
    });

    try {
      final applicationService = Provider.of<ApplicationService>(context, listen: false);
      _application.currentStep = _currentStep;
      await applicationService.saveDraft(_application);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Draft saved successfully'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving draft: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isDraftSaving = false;
        });
      }
    }
  }

  void _nextStep() {
    if (_validateCurrentStep()) {
      if (_currentStep < _totalSteps - 1) {
        setState(() {
          _currentStep++;
        });
        _pageController.nextPage(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
        );
        _saveDraft();
      } else {
        _submitApplication();
      }
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() {
        _currentStep--;
      });
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  bool _validateCurrentStep() {
    switch (_currentStep) {
      case 0:
        return _validatePersonalInfo();
      case 1:
        return _validateAdmissionDetails();
      case 2:
        return _validateDocuments();
      case 3:
        return _validateReview();
      default:
        return false;
    }
  }

  bool _validatePersonalInfo() {
    if (_application.applicantNameEnglish?.isEmpty ?? true) {
      _showError('English name is required');
      return false;
    }
    if (_application.applicantNameArabic?.isEmpty ?? true) {
      _showError('Arabic name is required');
      return false;
    }
    if (_application.nationalId?.isEmpty ?? true) {
      _showError('National ID is required');
      return false;
    }
    if (_application.email?.isEmpty ?? true) {
      _showError('Email is required');
      return false;
    }
    if (_application.phone?.isEmpty ?? true) {
      _showError('Phone number is required');
      return false;
    }
    return true;
  }

  bool _validateAdmissionDetails() {
    if (_application.programId == null) {
      _showError('Please select a program');
      return false;
    }
    if (_application.batchId == null) {
      _showError('Please select a batch');
      return false;
    }
    return true;
  }

  bool _validateDocuments() {
    if (_application.documents.isEmpty) {
      _showError('Please upload at least one document');
      return false;
    }
    return true;
  }

  bool _validateReview() {
    return _validatePersonalInfo() && _validateAdmissionDetails() && _validateDocuments();
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  Future<void> _submitApplication() async {
    if (!_validateReview()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final applicationService = Provider.of<ApplicationService>(context, listen: false);
      await applicationService.submitApplication(_application);
      
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/application-success');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error submitting application: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('New Application'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (_isDraftSaving)
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              ),
            )
          else
            IconButton(
              icon: const Icon(Icons.save),
              onPressed: _saveDraft,
              tooltip: 'Save Draft',
            ),
        ],
      ),
      body: Column(
        children: [
          // Step Indicator
          StepIndicator(
            currentStep: _currentStep,
            totalSteps: _totalSteps,
            stepTitles: _stepTitles,
          ),
          
          // Form Content
          Expanded(
            child: PageView(
              controller: _pageController,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                PersonalInfoStep(
                  application: _application,
                  onChanged: () => setState(() {}),
                ),
                AdmissionDetailsStep(
                  application: _application,
                  onChanged: () => setState(() {}),
                ),
                DocumentsStep(
                  application: _application,
                  onChanged: () => setState(() {}),
                ),
                ReviewStep(
                  application: _application,
                  onChanged: () => setState(() {}),
                ),
              ],
            ),
          ),
          
          // Navigation Buttons
          Container(
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.2),
                  spreadRadius: 1,
                  blurRadius: 5,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                if (_currentStep > 0)
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _previousStep,
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        side: const BorderSide(color: Colors.blue),
                      ),
                      child: const Text('Previous'),
                    ),
                  ),
                if (_currentStep > 0) const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _nextStep,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      backgroundColor: Colors.blue,
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : Text(_currentStep == _totalSteps - 1 ? 'Submit' : 'Next'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }
}