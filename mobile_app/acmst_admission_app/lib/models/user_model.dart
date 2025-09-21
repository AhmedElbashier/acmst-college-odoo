class User {
  final int id;
  final String name;
  final String email;
  final String phone;
  final String? nationalId;
  final String? profileImage;
  final DateTime? lastLogin;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  
  User({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    this.nationalId,
    this.profileImage,
    this.lastLogin,
    this.isActive = true,
    required this.createdAt,
    required this.updatedAt,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      nationalId: json['national_id'],
      profileImage: json['profile_image'],
      lastLogin: json['last_login'] != null 
          ? DateTime.parse(json['last_login']) 
          : null,
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'phone': phone,
      'national_id': nationalId,
      'profile_image': profileImage,
      'last_login': lastLogin?.toIso8601String(),
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
  
  User copyWith({
    int? id,
    String? name,
    String? email,
    String? phone,
    String? nationalId,
    String? profileImage,
    DateTime? lastLogin,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      nationalId: nationalId ?? this.nationalId,
      profileImage: profileImage ?? this.profileImage,
      lastLogin: lastLogin ?? this.lastLogin,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User && other.id == id;
  }
  
  @override
  int get hashCode => id.hashCode;
  
  @override
  String toString() {
    return 'User(id: $id, name: $name, email: $email, phone: $phone)';
  }
}