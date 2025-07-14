# Frontend Developer Daily Task Guide

## Role Overview
Frontend developers are responsible for user interface development, user experience optimization, client-side performance, and frontend architecture within the ccobservatory project. This guide outlines daily responsibilities, task templates, and quality standards.

## Daily Responsibilities

### Core Development Tasks
- **UI Component Development**: Create reusable, accessible React/Vue components
- **State Management**: Implement and maintain application state architecture
- **API Integration**: Connect frontend to backend services and handle data flow
- **Performance Optimization**: Optimize bundle size, loading times, and runtime performance
- **Cross-browser Compatibility**: Ensure consistent experience across browsers and devices
- **Accessibility Implementation**: Follow WCAG guidelines and implement inclusive design

### Daily Deliverables
1. **Component Updates**: Build/update 1-2 UI components per day
2. **Visual Design Implementation**: Convert designs to pixel-perfect interfaces
3. **Frontend Tests**: Maintain 75%+ test coverage for components and utilities
4. **Performance Monitoring**: Track and optimize Core Web Vitals metrics
5. **Accessibility Compliance**: Complete accessibility checklist for new features
6. **Documentation**: Update component library and style guide documentation

## Daily Task Templates

### Morning Routine (9:00-9:30 AM)
```
[ ] Check browser testing reports and cross-browser issues
[ ] Review failed frontend builds and fix blocking issues
[ ] Update task status in project management tool
[ ] Review pull requests assigned for UI/UX review
[ ] Check frontend performance metrics and Core Web Vitals
[ ] Test latest backend API changes in development environment
```

### Development Sprint Tasks
```
[ ] Implement [Component/Feature Name]
  [ ] Review design specifications and user stories
  [ ] Create component structure and props interface
  [ ] Implement responsive design and mobile optimization
  [ ] Add proper accessibility attributes and keyboard navigation
  [ ] Integrate with backend APIs and handle error states
  [ ] Write component tests and user interaction tests
  [ ] Update component documentation and style guide
  [ ] Performance test and optimize bundle impact
```

### UI/UX Review Checklist
```
[ ] Design matches specifications exactly
[ ] Component is responsive across all breakpoints
[ ] Accessibility standards are met (WCAG 2.1 AA)
[ ] Loading states and error handling are implemented
[ ] Color contrast meets accessibility requirements
[ ] Keyboard navigation works properly
[ ] Screen reader compatibility is verified
[ ] Performance impact is within acceptable limits
```

### End-of-Day Tasks (5:00-5:30 PM)
```
[ ] Commit and push all work-in-progress code
[ ] Update component library documentation
[ ] Check browser compatibility across major browsers
[ ] Update task status and add blockers/notes
[ ] Run accessibility audit on completed work
[ ] Plan next day's priorities and design reviews
```

## Communication Protocols

### Daily Standups (9:30-9:45 AM)
- **What I completed yesterday**: Specific components/features delivered
- **What I'm working on today**: UI priorities and design implementation status
- **Blockers and dependencies**: Design approvals, API dependencies, browser issues
- **UX insights**: User feedback, accessibility concerns, performance observations

### Weekly Design Reviews (Tuesdays 2:00-3:00 PM)
- Review upcoming design specifications and wireframes
- Discuss technical feasibility of design requirements
- Plan component architecture and reusability strategy
- Coordinate with design team on responsive and mobile considerations
- Review user feedback and usability testing results

### Frontend-Backend Sync (Thursdays 11:00-11:30 AM)
- **API Requirements**: Discuss data structure needs for frontend features
- **Integration Status**: Review API integration progress and issues
- **Performance Coordination**: Align on caching strategies and data optimization
- **Error Handling**: Establish consistent error response patterns

## Quality Standards

### Code Quality Requirements
- **Test Coverage**: Minimum 75% for components, 60% overall
- **Code Style**: Follow ESLint, Prettier, and team style guide
- **Component Architecture**: Reusable, composable, and well-documented components
- **Performance**: Bundle size increases <50KB per feature
- **Accessibility**: WCAG 2.1 AA compliance for all interactive elements
- **Browser Support**: Chrome, Firefox, Safari, Edge (last 2 versions)

### UI/UX Standards
- **Design Fidelity**: 95% pixel-perfect match to approved designs
- **Responsive Design**: Optimal experience on mobile, tablet, and desktop
- **Loading Performance**: First Contentful Paint <2s, Largest Contentful Paint <4s
- **Interaction Design**: Smooth animations and transitions (<16ms frame times)
- **User Feedback**: Clear loading states, error messages, and success indicators

### Accessibility Standards
- **Keyboard Navigation**: Full keyboard accessibility without mouse dependency
- **Screen Reader Support**: Proper ARIA labels and semantic HTML structure
- **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Focus Management**: Visible focus indicators and logical tab order
- **Alternative Content**: Alt text for images, captions for videos

## Tools and Resource Access

### Development Environment
- **Code Editor**: VS Code with frontend-specific extensions
- **Browser Tools**: Chrome DevTools, Firefox Developer Tools, Safari Web Inspector
- **Design Tools**: Figma, Sketch access for design specifications
- **Testing Tools**: Jest, React Testing Library, Cypress for E2E testing
- **Performance Tools**: Lighthouse, WebPageTest, Chrome Performance panel

### Required Access
- **Source Control**: GitHub repository with feature branch permissions
- **Design System**: Access to component library and style guide
- **CDN/Assets**: Image and asset management system access
- **Analytics**: Google Analytics, user behavior tracking tools
- **Browser Testing**: BrowserStack or Sauce Labs for cross-browser testing

### Communication Tools
- **Daily Communication**: Slack #frontend-dev channel
- **Design Collaboration**: Figma/InVision for design review and comments
- **Bug Tracking**: Frontend-specific issue tracking and browser compatibility
- **Documentation**: Component library documentation system

## Performance Metrics and KPIs

### Development Velocity
- **Story Points**: Complete 12-18 story points per sprint
- **Component Creation**: Build 3-5 reusable components per sprint
- **Design Implementation**: 90%+ design specification accuracy
- **Bug Resolution**: Resolve frontend bugs within 1 business day

### Technical Metrics
- **Core Web Vitals**: LCP <2.5s, FID <100ms, CLS <0.1
- **Bundle Size**: Keep main bundle under 250KB gzipped
- **Test Coverage**: Maintain 75%+ component test coverage
- **Accessibility Score**: 95%+ Lighthouse accessibility score

### User Experience Metrics
- **Page Load Speed**: 90% of pages load in <3 seconds
- **Mobile Performance**: Mobile Lighthouse score >90
- **Cross-browser Compatibility**: <5% browser-specific issues
- **Accessibility Compliance**: Zero WCAG violations in production

## Escalation Procedures

### Technical Issues
1. **Level 1**: Check component documentation and style guide (15 minutes)
2. **Level 2**: Consult frontend team Slack channel for quick assistance
3. **Level 3**: Escalate to senior frontend developer or UI lead
4. **Level 4**: Involve design team for UX/design clarification
5. **Level 5**: Engage backend team for API or integration issues

### Design and UX Issues
1. **Design Clarification**: Request clarification from design team via Figma comments
2. **Accessibility Concerns**: Consult with accessibility specialist or team lead
3. **Performance Issues**: Engage with performance engineer or senior developer
4. **User Feedback**: Route usability issues to product team and UX researcher

## Best Practices

### Development Workflow
- **Component-First Development**: Build reusable components before page-specific code
- **Mobile-First Design**: Start with mobile layout and progressively enhance
- **Performance Budget**: Monitor bundle size and performance impact of new features
- **Accessibility First**: Include accessibility considerations from the start
- **Progressive Enhancement**: Ensure core functionality works without JavaScript

### Code Organization
- **Atomic Design**: Organize components using atomic design principles
- **Style Consistency**: Use design tokens and consistent naming conventions
- **State Management**: Keep component state minimal and lift state appropriately
- **Testing Strategy**: Test component behavior, not implementation details

### Collaboration
- **Design Handoff**: Review designs thoroughly before implementation begins
- **Frontend Documentation**: Maintain up-to-date component library documentation
- **Cross-team Communication**: Regularly sync with backend team on API changes
- **User-Centered Development**: Consider user experience in all technical decisions

## Emergency Response

### Production UI Issues
```
[ ] Assess user impact and affected browsers/devices
[ ] Check error monitoring for frontend JavaScript errors
[ ] Identify if issue is frontend code or API related
[ ] Implement hotfix or rollback if necessary
[ ] Test fix across all supported browsers and devices
[ ] Monitor user behavior and error rates post-fix
[ ] Document issue and prevention strategies
```

### Performance Emergencies
```
[ ] Check Core Web Vitals and performance monitoring dashboards
[ ] Identify performance bottlenecks (network, JavaScript, rendering)
[ ] Implement immediate performance optimizations
[ ] Consider enabling performance budgets and monitoring
[ ] Coordinate with backend team if API performance is involved
[ ] Monitor user experience metrics post-optimization
```

### Accessibility Issues
```
[ ] Assess severity and user impact of accessibility barrier
[ ] Test with actual assistive technologies (screen readers, etc.)
[ ] Implement immediate accessibility fixes
[ ] Verify fixes with accessibility testing tools
[ ] Update accessibility testing procedures to prevent recurrence
[ ] Document accessibility requirements for future development
```

## Component Development Standards

### Component Structure
```javascript
// Component template structure
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

const ComponentName = ({ 
  prop1, 
  prop2, 
  className,
  children,
  ...rest 
}) => {
  // Component logic here
  
  return (
    <StyledWrapper 
      className={className}
      role="appropriate-role"
      aria-label="descriptive-label"
      {...rest}
    >
      {children}
    </StyledWrapper>
  );
};

ComponentName.propTypes = {
  prop1: PropTypes.string.isRequired,
  prop2: PropTypes.number,
  className: PropTypes.string,
  children: PropTypes.node,
};

ComponentName.defaultProps = {
  prop2: 0,
  className: '',
  children: null,
};

export default ComponentName;
```

### Testing Standards
```javascript
// Component test template
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ComponentName from './ComponentName';

describe('ComponentName', () => {
  it('renders with required props', () => {
    render(<ComponentName prop1="test" />);
    expect(screen.getByRole('appropriate-role')).toBeInTheDocument();
  });

  it('handles user interactions correctly', async () => {
    const user = userEvent.setup();
    const mockCallback = jest.fn();
    
    render(<ComponentName prop1="test" onClick={mockCallback} />);
    
    await user.click(screen.getByRole('button'));
    expect(mockCallback).toHaveBeenCalledTimes(1);
  });

  it('meets accessibility requirements', () => {
    render(<ComponentName prop1="test" />);
    
    const element = screen.getByRole('appropriate-role');
    expect(element).toHaveAttribute('aria-label');
    expect(element).toBeVisible();
  });
});
```

This guide ensures frontend developers maintain high code quality, design fidelity, and optimal user experience while building the ccobservatory project's client-side application.