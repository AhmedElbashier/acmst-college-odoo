import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:local_auth/local_auth.dart';
import 'package:crypto/crypto.dart';
import 'package:http/http.dart' as http;

import '../models/user_model.dart';
import '../utils/app_constants.dart';

class AuthService extends ChangeNotifier {
  User? _currentUser;
  String? _token;
  bool _isLoading = false;
  String? _error;
  bool _biometricEnabled = false;
  
  // Getters
  User? get currentUser => _currentUser;
  String? get token => _token;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _currentUser != null && _token != null;
  bool get biometricEnabled => _biometricEnabled;
  
  // Local Authentication
  final LocalAuthentication _localAuth = LocalAuthentication();
  
  AuthService() {
    _initializeAuth();
  }
  
  Future<void> _initializeAuth() async {
    await _loadStoredAuth();
    await _checkBiometricAvailability();
  }
  
  Future<void> _loadStoredAuth() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString(AppConstants.userTokenKey);
      final userData = prefs.getString(AppConstants.userDataKey);
      final biometricEnabled = prefs.getBool(AppConstants.biometricEnabledKey) ?? false;
      
      if (token != null && userData != null) {
        _token = token;
        _currentUser = User.fromJson(jsonDecode(userData));
        _biometricEnabled = biometricEnabled;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading stored auth: $e');
    }
  }
  
  Future<void> _checkBiometricAvailability() async {
    try {
      final isAvailable = await _localAuth.canCheckBiometrics;
      final isDeviceSupported = await _localAuth.isDeviceSupported;
      
      if (isAvailable && isDeviceSupported) {
        final availableBiometrics = await _localAuth.getAvailableBiometrics();
        _biometricEnabled = availableBiometrics.isNotEmpty;
      }
    } catch (e) {
      debugPrint('Error checking biometric availability: $e');
    }
  }
  
  Future<bool> login({
    required String email,
    required String password,
    bool useBiometric = false,
  }) async {
    _setLoading(true);
    _clearError();
    
    try {
      if (useBiometric && _biometricEnabled) {
        final authenticated = await _authenticateWithBiometric();
        if (!authenticated) {
          _setError('Biometric authentication failed');
          return false;
        }
      }
      
      // Make API call to login
      final response = await _performLogin(email, password);
      
      if (response['success'] == true) {
        _token = response['token'];
        _currentUser = User.fromJson(response['user']);
        
        // Store auth data
        await _storeAuthData();
        
        // Enable biometric if requested
        if (useBiometric && _biometricEnabled) {
          await _enableBiometric();
        }
        
        notifyListeners();
        return true;
      } else {
        _setError(response['message'] ?? 'Login failed');
        return false;
      }
    } catch (e) {
      _setError('Network error: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }
  
  Future<Map<String, dynamic>> _performLogin(String email, String password) async {
    final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}${AppConstants.authEndpoint}/login');
    
    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode({
        'email': email,
        'password': password,
        'device_type': 'mobile',
        'device_id': await _getDeviceId(),
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }
  
  Future<bool> _authenticateWithBiometric() async {
    try {
      return await _localAuth.authenticate(
        localizedReason: 'Please authenticate to access your account',
        options: const AuthenticationOptions(
          biometricOnly: true,
          stickyAuth: true,
        ),
      );
    } catch (e) {
      debugPrint('Biometric authentication error: $e');
      return false;
    }
  }
  
  Future<void> _enableBiometric() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(AppConstants.biometricEnabledKey, true);
      _biometricEnabled = true;
    } catch (e) {
      debugPrint('Error enabling biometric: $e');
    }
  }
  
  Future<void> _storeAuthData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConstants.userTokenKey, _token!);
      await prefs.setString(AppConstants.userDataKey, jsonEncode(_currentUser!.toJson()));
    } catch (e) {
      debugPrint('Error storing auth data: $e');
    }
  }
  
  Future<String> _getDeviceId() async {
    // Generate a unique device ID
    final timestamp = DateTime.now().millisecondsSinceEpoch.toString();
    final random = (timestamp.hashCode % 1000000).toString();
    return '${timestamp}_$random';
  }
  
  Future<bool> register({
    required String name,
    required String email,
    required String password,
    required String phone,
    required String nationalId,
  }) async {
    _setLoading(true);
    _clearError();
    
    try {
      final response = await _performRegistration(
        name: name,
        email: email,
        password: password,
        phone: phone,
        nationalId: nationalId,
      );
      
      if (response['success'] == true) {
        _setError(null);
        return true;
      } else {
        _setError(response['message'] ?? 'Registration failed');
        return false;
      }
    } catch (e) {
      _setError('Network error: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }
  
  Future<Map<String, dynamic>> _performRegistration({
    required String name,
    required String email,
    required String password,
    required String phone,
    required String nationalId,
  }) async {
    final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}${AppConstants.authEndpoint}/register');
    
    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode({
        'name': name,
        'email': email,
        'password': password,
        'phone': phone,
        'national_id': nationalId,
        'device_type': 'mobile',
        'device_id': await _getDeviceId(),
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }
  
  Future<void> logout() async {
    _setLoading(true);
    
    try {
      // Call logout API if token exists
      if (_token != null) {
        await _performLogout();
      }
    } catch (e) {
      debugPrint('Logout API error: $e');
    } finally {
      // Clear local data
      await _clearAuthData();
      _currentUser = null;
      _token = null;
      _biometricEnabled = false;
      _setLoading(false);
      notifyListeners();
    }
  }
  
  Future<void> _performLogout() async {
    final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}${AppConstants.authEndpoint}/logout');
    
    await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer $_token',
      },
    );
  }
  
  Future<void> _clearAuthData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(AppConstants.userTokenKey);
      await prefs.remove(AppConstants.userDataKey);
      await prefs.remove(AppConstants.biometricEnabledKey);
    } catch (e) {
      debugPrint('Error clearing auth data: $e');
    }
  }
  
  Future<bool> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    _setLoading(true);
    _clearError();
    
    try {
      final response = await _performPasswordChange(currentPassword, newPassword);
      
      if (response['success'] == true) {
        _setError(null);
        return true;
      } else {
        _setError(response['message'] ?? 'Password change failed');
        return false;
      }
    } catch (e) {
      _setError('Network error: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }
  
  Future<Map<String, dynamic>> _performPasswordChange(String currentPassword, String newPassword) async {
    final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}${AppConstants.authEndpoint}/change-password');
    
    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer $_token',
      },
      body: jsonEncode({
        'current_password': currentPassword,
        'new_password': newPassword,
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }
  
  Future<bool> forgotPassword(String email) async {
    _setLoading(true);
    _clearError();
    
    try {
      final response = await _performForgotPassword(email);
      
      if (response['success'] == true) {
        _setError(null);
        return true;
      } else {
        _setError(response['message'] ?? 'Password reset failed');
        return false;
      }
    } catch (e) {
      _setError('Network error: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }
  
  Future<Map<String, dynamic>> _performForgotPassword(String email) async {
    final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}${AppConstants.authEndpoint}/forgot-password');
    
    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode({
        'email': email,
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }
  
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  void _setError(String? error) {
    _error = error;
    notifyListeners();
  }
  
  void _clearError() {
    _error = null;
    notifyListeners();
  }
  
  void clearError() {
    _clearError();
  }
}