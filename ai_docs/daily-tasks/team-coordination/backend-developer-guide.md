# Backend Developer Daily Task Guide

## Role Overview
Backend developers are responsible for server-side logic, API development, database management, and system architecture within the ccobservatory project. This guide outlines daily responsibilities, task templates, and quality standards.

## Daily Responsibilities

### Core Development Tasks
- **API Development**: Design and implement RESTful APIs and GraphQL endpoints
- **Database Management**: Design schemas, optimize queries, manage migrations
- **Business Logic**: Implement core application logic and data processing
- **Integration Services**: Connect external APIs and third-party services
- **Performance Optimization**: Monitor and optimize server response times
- **Security Implementation**: Apply authentication, authorization, and data protection

### Daily Deliverables
1. **Code Commits**: Minimum 2-3 meaningful commits with clear messages
2. **API Documentation**: Update OpenAPI/Swagger docs for new endpoints
3. **Unit Tests**: Maintain 80%+ code coverage for new features
4. **Performance Metrics**: Log and monitor API response times
5. **Security Reviews**: Complete security checklist for new code
6. **Database Changes**: Document schema changes and migration scripts

## Daily Task Templates

### Morning Routine (9:00-9:30 AM)
```
[ ] Check overnight monitoring alerts and system health
[ ] Review failed CI/CD pipelines and fix blocking issues
[ ] Update task status in project management tool
[ ] Review pull requests assigned for code review
[ ] Check database performance metrics and slow queries
[ ] Respond to urgent support tickets or bug reports
```

### Development Sprint Tasks
```
[ ] Implement [Feature/Endpoint Name]
  [ ] Design API specification
  [ ] Create database schema changes
  [ ] Implement business logic
  [ ] Add comprehensive error handling
  [ ] Write unit and integration tests
  [ ] Update API documentation
  [ ] Performance test endpoints
  [ ] Security review and validation
```

### Code Review Checklist
```
[ ] Code follows project style guidelines
[ ] Business logic is properly abstracted
[ ] Error handling is comprehensive
[ ] Security best practices are followed
[ ] Database queries are optimized
[ ] Tests cover happy path and edge cases
[ ] API documentation is updated
[ ] Performance implications are considered
```

### End-of-Day Tasks (5:00-5:30 PM)
```
[ ] Commit and push all work-in-progress code
[ ] Update task status and add blockers/notes
[ ] Review monitoring dashboards for issues
[ ] Plan next day's priorities
[ ] Update team on progress and blockers
[ ] Backup critical work and configurations
```

## Communication Protocols

### Daily Standups (9:30-9:45 AM)
- **What I completed yesterday**: Specific features/fixes delivered
- **What I'm working on today**: Clear priorities and estimated completion
- **Blockers and dependencies**: Technical issues, waiting for reviews/approvals
- **System health updates**: Performance issues, security concerns, outages

### Weekly Planning Sessions (Mondays 10:00-11:00 AM)
- Review sprint backlog and story priorities
- Estimate effort for new user stories
- Identify technical dependencies and risks
- Plan database migrations and deployment windows
- Coordinate with frontend team on API requirements

### Code Review Process
- **Response Time**: Review pull requests within 4 hours
- **Review Depth**: Check functionality, security, performance, and style
- **Feedback Quality**: Provide constructive, specific suggestions
- **Follow-up**: Re-review within 2 hours of updates

## Quality Standards

### Code Quality Requirements
- **Test Coverage**: Minimum 80% for new code, 70% overall
- **Code Style**: Follow ESLint/Prettier configurations
- **Documentation**: All public APIs documented with examples
- **Error Handling**: Comprehensive error responses with proper HTTP codes
- **Security**: All inputs validated, SQL injection prevention, rate limiting
- **Performance**: API responses under 200ms for simple queries

### Database Standards
- **Schema Design**: Normalized structure with proper relationships
- **Indexing**: Query performance under 50ms for common operations
- **Migrations**: Reversible migrations with proper rollback procedures
- **Backup**: Daily automated backups with recovery testing
- **Security**: Encrypted connections, least privilege access

### API Standards
- **RESTful Design**: Follow REST principles and HTTP semantics
- **Versioning**: Maintain backward compatibility, clear deprecation policies
- **Documentation**: OpenAPI 3.0 specification with examples
- **Error Responses**: Consistent error format with helpful messages
- **Rate Limiting**: Implement appropriate limits per endpoint
- **Authentication**: Secure JWT implementation with proper expiration

## Tools and Resource Access

### Development Environment
- **IDE/Editor**: VS Code with recommended extensions
- **Database Tools**: DBeaver, pgAdmin, Redis CLI
- **API Testing**: Postman collections, Insomnia, curl scripts
- **Monitoring**: New Relic, DataDog, application-specific dashboards
- **Debugging**: Chrome DevTools, server-side debuggers

### Required Access
- **Source Control**: GitHub repository with development branch access
- **Databases**: Development, staging, and read-only production access
- **CI/CD**: Jenkins/GitHub Actions build and deployment permissions
- **Monitoring**: Read access to production monitoring systems
- **Documentation**: Confluence, Notion, or team wiki write access

### Communication Tools
- **Daily Communication**: Slack #backend-dev channel
- **Video Meetings**: Zoom/Teams for standups and planning
- **Documentation**: Shared team knowledge base
- **Issue Tracking**: Jira, Linear, or GitHub Issues

## Performance Metrics and KPIs

### Development Velocity
- **Story Points**: Complete 15-20 story points per sprint
- **Code Quality**: Maintain <5% bug discovery rate
- **Review Turnaround**: Complete code reviews within 4 hours
- **Deployment Success**: 95%+ successful deployments

### Technical Metrics
- **API Performance**: 95th percentile response time <500ms
- **Uptime**: 99.9% service availability
- **Test Coverage**: Maintain 80%+ code coverage
- **Security**: Zero critical vulnerabilities in production

### Collaboration Metrics
- **Knowledge Sharing**: Document 1 technical solution per week
- **Mentoring**: Support junior developers with code reviews
- **Cross-team Coordination**: Attend frontend sync meetings weekly
- **Process Improvement**: Suggest 1 process improvement per month

## Escalation Procedures

### Technical Issues
1. **Level 1**: Self-troubleshooting and documentation review (30 minutes)
2. **Level 2**: Consult team Slack channel for quick assistance
3. **Level 3**: Escalate to senior backend developer or tech lead
4. **Level 4**: Involve DevOps team for infrastructure issues
5. **Level 5**: Page on-call engineer for production outages

### Process Issues
1. **Blocked on Dependencies**: Notify project manager and affected teams
2. **Scope Changes**: Discuss with product owner and tech lead
3. **Resource Constraints**: Escalate to engineering manager
4. **Team Conflicts**: Work with scrum master or team lead

## Best Practices

### Development Workflow
- **Feature Branches**: Use descriptive branch names with ticket numbers
- **Commit Messages**: Follow conventional commit format
- **Testing**: Write tests before implementation (TDD approach)
- **Documentation**: Update docs with code changes
- **Security**: Never commit secrets, use environment variables

### Collaboration
- **Async Communication**: Use threads and detailed messages
- **Knowledge Sharing**: Maintain team runbooks and troubleshooting guides
- **Cross-functional Work**: Collaborate early with frontend and DevOps teams
- **Continuous Learning**: Stay updated with backend technology trends

## Emergency Response

### Production Issues
```
[ ] Assess severity and impact immediately
[ ] Notify on-call rotation and incident manager
[ ] Begin triage and root cause analysis
[ ] Implement immediate mitigation if possible
[ ] Document all actions and timeline
[ ] Coordinate with DevOps for infrastructure fixes
[ ] Prepare rollback plan if necessary
[ ] Post-incident: Complete root cause analysis
```

### Security Incidents
```
[ ] Immediately secure affected systems
[ ] Notify security team and management
[ ] Preserve evidence and audit logs
[ ] Assess data breach potential
[ ] Coordinate with legal/compliance if required
[ ] Implement fixes and security patches
[ ] Document incident and response actions
```

This guide ensures backend developers maintain high productivity, code quality, and effective team collaboration while supporting the ccobservatory project's technical requirements.