# ACMST College Odoo Modules Localization Guide

This document explains how to use the Arabic and English localization features implemented in the ACMST College Odoo modules.

## 🌍 Supported Languages

The ACMST College management system supports two languages:

- **English** (Default) - `en`
- **Arabic** - `ar`

## 📁 Localization Files Structure

```
acmst-college-odoo/
├── addons/
│   ├── acmst_core_settings/
│   │   └── i18n/
│   │       ├── acmst_core_settings.pot  # Template file
│   │       ├── ar.po                   # Arabic translations
│   │       └── en.po                   # English translations
│   └── acmst_admission/
│       └── i18n/
│           ├── acmst_admission.pot     # Template file
│           ├── ar.po                   # Arabic translations
│           └── en.po                   # English translations
```

## 🚀 Installation and Setup

### Step 1: Install the Modules

1. **Using Docker (Recommended)**:
   ```bash
   docker-compose up -d
   ```
   Access Odoo at `http://localhost:8069`

2. **Manual Installation**:
   - Copy both modules to your Odoo addons directory
   - Update Odoo configuration to include the modules

### Step 2: Install Required Modules

1. Login to Odoo as administrator
2. Go to **Apps** menu
3. Search for and install:
   - **ACMST Core Settings** (install first)
   - **ACMST Admission Management** (install second)

### Step 3: Configure Languages

1. Go to **Settings > Translations > Languages**
2. Search for "Arabic" and activate it
3. Set Arabic as the default language if needed

### Step 4: Import Translation Files

1. Go to **Settings > Translations > Import Translation**
2. Upload the translation files:
   - `addons/acmst_core_settings/i18n/ar.po`
   - `addons/acmst_core_settings/i18n/en.po`
   - `addons/acmst_admission/i18n/ar.po`
   - `addons/acmst_admission/i18n/en.po`
3. Select the appropriate language for each file
4. Click **Import**

### Step 5: Update Translations

1. Go to **Settings > Translations > Application Terms > Export Translation**
2. Select the modules: `acmst_core_settings` and `acmst_admission`
3. Choose language: Arabic or English
4. Export to get the latest translation files
5. Edit the .po files with a text editor
6. Re-import the updated files

## 👤 User Language Configuration

### For Individual Users

1. Click on your **username** in the top right corner
2. Go to **Preferences**
3. In the **Language** field, select:
   - **English** for English interface
   - **Arabic** for Arabic interface
4. Click **Save**

### For Administrators

To set default language for all users:

1. Go to **Settings > General Settings**
2. Scroll to **Languages** section
3. Set **Default Language** to Arabic or English
4. Click **Save**

## 📝 Translation Files Format

### .pot Files (Templates)

Template files contain all translatable strings without translations:
```po
msgid "University"
msgstr ""
```

### .po Files (Translations)

Translation files contain both original strings and their translations:
```po
msgid "University"
msgstr "الجامعة"
```

## 🎯 Translatable Content

The localization system covers:

### Core Settings Module
- University management interface
- College management interface
- Program management interface
- Batch management interface
- Academic year management
- Academic rules management
- Menu items and labels
- Button labels and actions
- Field labels and descriptions

### Admission Management Module
- Admission application interface
- Health check forms
- Workflow management
- Coordinator conditions
- Portal application forms
- Student portal interface
- Report labels and headers

### Portal Templates
- Admission portal home page
- Application forms
- Status tracking pages
- Contact information
- Navigation menus

## 🔧 Adding New Translations

### For Developers

1. **Add new translatable strings** in Python code:
   ```python
   from odoo import _
   message = _("Your message here")
   ```

2. **Add new translatable strings** in XML views:
   ```xml
   <field name="name" string="Your Label"/>
   ```

3. **Update translation files**:
   ```bash
   # Generate new .pot files
   python odoo/tools/translation.py --module=acmst_core_settings --template

   # Update existing .po files
   msgmerge ar.po acmst_core_settings.pot -o ar.po
   ```

### For Translators

1. Open the .po file with a text editor or translation tool
2. Find untranslated strings (empty `msgstr`)
3. Add the translation in the appropriate language
4. Save the file
5. Import the updated file in Odoo

## 🧪 Testing Localization

### Test Interface Language

1. Change your user language preference
2. Navigate through different modules
3. Verify that all text appears in the selected language
4. Check both backend (Odoo interface) and frontend (portal)

### Test Portal Localization

1. Access the admission portal: `http://localhost:8069/admission`
2. Check that portal text is translated
3. Test form labels and messages
4. Verify right-to-left (RTL) layout for Arabic

### Test Module-Specific Content

1. **Core Settings**: Create/edit universities, colleges, programs
2. **Admission**: Submit applications, check health forms
3. **Reports**: Generate reports and check translated headers
4. **Menus**: Navigate through menus and check labels

## 🐛 Troubleshooting

### Common Issues

#### Translations Not Appearing
1. **Check file import**: Ensure .po files are imported correctly
2. **Check language activation**: Verify Arabic is activated in languages
3. **Check user preferences**: Ensure user language is set correctly
4. **Clear cache**: Restart Odoo server to refresh translations

#### Missing Translations
1. **Export latest**: Export current translations from Odoo
2. **Add missing**: Add translations for new strings
3. **Import updated**: Import the updated translation files

#### Portal Not Localized
1. **Check template files**: Ensure portal templates use translation functions
2. **Restart web server**: Restart Odoo to refresh portal cache
3. **Check browser cache**: Clear browser cache

### Debug Mode

Enable developer mode to see translation status:
1. Go to **Settings > General Settings**
2. Enable **Developer Mode**
3. Go to **Settings > Translations > Application Terms**
4. Check translation coverage for each module

## 📊 Translation Statistics

### Core Settings Module
- **Total Strings**: ~150+
- **Arabic Coverage**: 100%
- **English Coverage**: 100%
- **Last Updated**: 2025-01-01

### Admission Management Module
- **Total Strings**: ~300+
- **Arabic Coverage**: 100%
- **English Coverage**: 100%
- **Last Updated**: 2025-01-01

## 🔄 Maintenance

### Regular Updates

1. **After code changes**: Update .pot files and translate new strings
2. **Monthly review**: Review translation quality and consistency
3. **User feedback**: Incorporate user suggestions for better translations
4. **Backup translations**: Keep backup copies of translation files

### Version Control

Translation files should be included in version control:
- Commit .po files with code changes
- Track translation progress in project management
- Use translation memory tools for consistency

## 📞 Support

For localization support:

- **Technical Issues**: Contact development team
- **Translation Quality**: Submit feedback via Odoo interface
- **New Languages**: Request additional language support

---

**Note**: This localization system provides a solid foundation for multi-language support. Regular maintenance and updates will ensure the best user experience for both English and Arabic users.
