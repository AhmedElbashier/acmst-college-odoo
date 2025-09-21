class AppConstants {
  // App Information
  static const String appName = 'ACMST Admission';
  static const String appVersion = '1.0.0';
  static const String appBuildNumber = '1';
  
  // API Configuration
  static const String baseUrl = 'https://your-odoo-instance.com';
  static const String apiVersion = '/api/v1';
  static const String authEndpoint = '/auth';
  static const String admissionEndpoint = '/admission';
  
  // Storage Keys
  static const String userTokenKey = 'user_token';
  static const String userDataKey = 'user_data';
  static const String biometricEnabledKey = 'biometric_enabled';
  static const String themeModeKey = 'theme_mode';
  static const String languageKey = 'language';
  
  // Animation Durations
  static const Duration shortAnimation = Duration(milliseconds: 300);
  static const Duration mediumAnimation = Duration(milliseconds: 500);
  static const Duration longAnimation = Duration(milliseconds: 800);
  
  // File Upload
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
  static const List<String> allowedImageTypes = ['jpg', 'jpeg', 'png'];
  static const List<String> allowedDocumentTypes = ['pdf', 'doc', 'docx'];
  
  // Validation
  static const int minPasswordLength = 8;
  static const int maxNameLength = 50;
  static const int maxDescriptionLength = 500;
  
  // UI Constants
  static const double defaultPadding = 16.0;
  static const double defaultRadius = 8.0;
  static const double defaultElevation = 2.0;
  
  // Error Messages
  static const String networkError = 'Network connection error. Please check your internet connection.';
  static const String serverError = 'Server error. Please try again later.';
  static const String unknownError = 'An unknown error occurred. Please try again.';
  static const String validationError = 'Please check your input and try again.';
  
  // Success Messages
  static const String loginSuccess = 'Login successful!';
  static const String logoutSuccess = 'Logout successful!';
  static const String applicationSubmitted = 'Application submitted successfully!';
  static const String dataSaved = 'Data saved successfully!';
  
  // Status Messages
  static const String loading = 'Loading...';
  static const String saving = 'Saving...';
  static const String submitting = 'Submitting...';
  static const String processing = 'Processing...';
}