# Accessibility Guide

Claude Code Observatory is designed to be fully accessible and compliant with WCAG 2.1 AA standards. This guide covers the accessibility features available and how to use them effectively.

## Overview

Our commitment to accessibility ensures that Claude Code Observatory can be used by everyone, including people who rely on assistive technologies such as screen readers, voice recognition software, or keyboard-only navigation.

## Accessibility Features

### Keyboard Navigation

The entire application can be navigated using only a keyboard:

- **Tab**: Move forward through interactive elements
- **Shift + Tab**: Move backward through interactive elements  
- **Enter**: Activate buttons and links
- **Space**: Activate buttons and toggle controls
- **Escape**: Close modals, menus, and overlays
- **Arrow Keys**: Navigate within menus and lists

#### Skip Links

Skip links appear at the top of each page when using keyboard navigation:

- **Skip to main content**: Jump directly to the page's main content area
- **Skip to navigation**: Jump directly to the navigation menu

To reveal skip links:
1. Press `Tab` when the page loads
2. The skip links will become visible and focused
3. Press `Enter` to activate them

### Screen Reader Support

The application provides comprehensive screen reader support:

#### ARIA Implementation

- **aria-label**: Provides accessible names for interactive elements
- **aria-describedby**: Links elements to their descriptions
- **aria-live**: Announces dynamic content changes
- **aria-expanded**: Indicates expanded/collapsed state
- **aria-current**: Indicates current page/item in navigation
- **role attributes**: Defines element purposes for screen readers

#### Live Regions

Dynamic content changes are announced to screen readers:

- **Data loading**: "Loading dashboard data"
- **Errors**: "Error: Cannot connect to backend API"  
- **Success**: "Data loaded successfully"
- **Navigation**: "Navigated to Settings page"
- **Modal states**: "Modal opened/closed"

#### Semantic Structure

The application uses proper semantic HTML:

- `<header>`: Page and section headers
- `<nav>`: Navigation menus
- `<main>`: Main content area
- `<section>`: Content sections
- `<article>`: Individual conversations/items
- Proper heading hierarchy (h1 → h2 → h3)

### Visual Accessibility

#### Color and Contrast

- **WCAG AA Compliance**: All text meets 4.5:1 contrast ratio minimum
- **Color Independence**: Information is not conveyed by color alone
- **Built-in Audit Tool**: Color contrast verification available in Settings

#### Focus Management

- **Visible Focus Indicators**: Clear visual focus indicators on all interactive elements
- **Focus Trapping**: Modal dialogs properly trap focus within their boundaries
- **Focus Restoration**: Focus returns to triggering elements when modals close
- **Logical Tab Order**: Keyboard navigation follows the visual layout

#### Responsive Design

- **Zoom Support**: Content remains functional when zoomed up to 200%
- **Mobile Accessibility**: Touch targets meet minimum size requirements
- **Flexible Layouts**: Content reflows appropriately at different screen sizes

### Theme Support

The application supports both light and dark themes:

- **System Preference**: Automatically detects system dark/light mode preference
- **Manual Toggle**: Users can manually switch between themes
- **Screen Reader Announcements**: Theme changes are announced
- **Persistent Settings**: Theme preference is saved across sessions

## Using Accessibility Features

### For Keyboard Users

1. **Starting Navigation**:
   - Press `Tab` to reveal skip links
   - Use skip links to jump to main content or navigation
   
2. **Navigating Pages**:
   - Use `Tab`/`Shift+Tab` to move between interactive elements
   - Press `Enter` or `Space` to activate buttons
   - Use arrow keys within menus and lists
   
3. **Working with Modals**:
   - Press `Escape` to close modals
   - Focus is automatically trapped within open modals
   - Focus returns to the triggering element when closed

### For Screen Reader Users

1. **Page Structure**:
   - Use heading navigation (1-6) to scan page structure
   - Navigate by landmarks (header, nav, main, etc.)
   - Use the navigation menu for quick access to sections
   
2. **Live Updates**:
   - Status changes are automatically announced
   - Loading states and errors are communicated
   - Form validation errors are announced immediately
   
3. **Interactive Elements**:
   - All buttons and links have descriptive labels
   - Form fields are properly labeled and described
   - Tables include headers and captions where appropriate

### Accessibility Settings

Visit the **Settings** page to configure accessibility options:

1. **Theme Toggle**: Switch between light and dark themes
2. **Color Contrast Audit**: Run WCAG compliance checks
3. **Accessibility Help**: View this guide and keyboard shortcuts
4. **Screen Reader Options**: Configure announcement preferences

## Testing Accessibility

### Automated Testing

The application includes comprehensive accessibility testing:

```bash
# Run accessibility tests
npm run test:accessibility

# Run specific accessibility checks
npx playwright test tests/accessibility/comprehensive.spec.ts
```

### Manual Testing Checklist

#### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Skip links appear and function correctly
- [ ] All functionality available via keyboard
- [ ] Focus indicators are clearly visible
- [ ] Tab order is logical and intuitive

#### Screen Reader Testing
- [ ] Page structure is announced correctly
- [ ] All content is accessible to screen readers
- [ ] Dynamic content changes are announced
- [ ] Forms are properly labeled and described
- [ ] Error messages are announced immediately

#### Visual Testing
- [ ] Content is readable at 200% zoom
- [ ] Focus indicators meet contrast requirements
- [ ] Color is not the only way information is conveyed
- [ ] Text has sufficient contrast against backgrounds

### Testing Tools

#### Browser Extensions
- **axe DevTools**: Comprehensive accessibility testing
- **WAVE**: Web accessibility evaluation
- **Lighthouse**: Includes accessibility audit

#### Screen Readers
- **NVDA** (Windows): Free, comprehensive screen reader
- **JAWS** (Windows): Professional screen reader
- **VoiceOver** (macOS): Built-in screen reader
- **Orca** (Linux): Free screen reader

## WCAG 2.1 AA Compliance

Claude Code Observatory meets WCAG 2.1 AA standards:

### Level A Requirements
- ✅ Non-text content has text alternatives
- ✅ Media has captions and transcripts
- ✅ Content is presented without loss of meaning
- ✅ Functionality is available via keyboard
- ✅ Content doesn't cause seizures
- ✅ Users can navigate and find content

### Level AA Requirements  
- ✅ Captions for live media
- ✅ Audio descriptions for video
- ✅ Color contrast ratio of at least 4.5:1
- ✅ Text can be resized up to 200%
- ✅ Functionality available via keyboard
- ✅ No keyboard traps
- ✅ Timing is adjustable
- ✅ Moving content can be paused
- ✅ Page has titles and headings
- ✅ Focus is visible
- ✅ Language is identified
- ✅ Context changes are predictable
- ✅ Input errors are identified and described

## Developer Guidelines

### Creating Accessible Components

When building new components, ensure:

1. **Semantic HTML**: Use appropriate HTML elements
2. **ARIA Attributes**: Add ARIA labels where needed
3. **Keyboard Support**: Implement keyboard event handlers
4. **Focus Management**: Handle focus properly
5. **Screen Reader Testing**: Test with actual screen readers

### Example: Accessible Button

```svelte
<script>
  import { createEventDispatcher } from 'svelte';
  import { handleEnterKey, handleSpaceKey } from '$lib/utils/accessibility';
  
  export let disabled = false;
  export let ariaLabel = '';
  
  const dispatch = createEventDispatcher();
  
  function handleClick() {
    if (!disabled) {
      dispatch('click');
    }
  }
</script>

<button
  class="btn"
  {disabled}
  aria-label={ariaLabel}
  on:click={handleClick}
  on:keydown={handleEnterKey(handleClick)}
  on:keydown={handleSpaceKey(handleClick)}
>
  <slot />
</button>
```

### Accessibility Checklist for New Features

- [ ] Semantic HTML structure
- [ ] Proper ARIA attributes
- [ ] Keyboard navigation support
- [ ] Screen reader announcements
- [ ] Color contrast compliance
- [ ] Focus management
- [ ] Error handling and validation
- [ ] Automated tests included
- [ ] Manual testing completed

## Getting Help

### Reporting Accessibility Issues

If you encounter accessibility barriers:

1. **GitHub Issues**: Create an issue with the "accessibility" label
2. **Include Details**: 
   - Your assistive technology and version
   - Steps to reproduce the issue
   - Expected vs. actual behavior
3. **Screenshots/Videos**: If helpful for understanding the issue

### Resources

- **WCAG Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
- **Screen Reader Testing**: https://webaim.org/articles/screenreader_testing/
- **Keyboard Testing**: https://webaim.org/articles/keyboard/
- **Color Contrast**: https://webaim.org/resources/contrastchecker/

## Continuous Improvement

Accessibility is an ongoing commitment. We regularly:

- Audit the application for accessibility issues
- Update components based on user feedback
- Stay current with accessibility best practices
- Include accessibility in all new feature development

Your feedback helps us improve. Please report any accessibility barriers you encounter so we can address them promptly.