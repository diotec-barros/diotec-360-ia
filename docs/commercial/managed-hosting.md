# Managed Hosting (SaaS)

## Overview

Aethel Managed Hosting provides a fully-managed, production-ready deployment of the Diotec360 protocol. While the Core Diotec360 language and runtime are open source and free to self-host, our managed service offers enterprise-grade infrastructure, security, and support for organizations that need mission-critical reliability.

## Value Propositions

### Security Updates

- **Automatic Security Patches**: All security updates applied within 24 hours of disclosure
- **Zero-Downtime Updates**: Rolling updates ensure continuous availability
- **Vulnerability Monitoring**: 24/7 security monitoring and threat detection
- **Compliance Certifications**: SOC 2 Type II, ISO 27001, and PCI DSS compliance
- **Dedicated Security Team**: Expert security engineers monitoring your deployment

### Monitoring & Observability

- **Real-Time Metrics**: Comprehensive dashboards for proof generation, transaction throughput, and system health
- **Custom Alerts**: Configurable alerting for performance degradation, errors, and security events
- **Distributed Tracing**: End-to-end visibility into transaction flows and proof verification
- **Log Aggregation**: Centralized logging with advanced search and analysis
- **Performance Analytics**: Historical trends and capacity planning insights

### Compliance Support

- **Audit Trail Generation**: Automated compliance reporting for regulatory requirements
- **Data Residency**: Deploy in specific geographic regions to meet data sovereignty requirements
- **Retention Policies**: Configurable data retention and archival policies
- **Compliance Documentation**: Pre-built templates for SOX, GDPR, and financial regulations
- **Third-Party Audits**: Regular independent security and compliance audits

### SLA Guarantees

- **99.99% Uptime SLA**: Financial credits for any downtime below SLA threshold
- **Performance Guarantees**: Committed latency and throughput targets
- **Support Response Times**: 
  - Critical issues: 15-minute response
  - High priority: 1-hour response
  - Normal priority: 4-hour response
- **Disaster Recovery**: RPO < 1 hour, RTO < 4 hours
- **Multi-Region Redundancy**: Automatic failover across availability zones

## Deployment Comparison

### Self-Hosted vs Managed

| Feature | Self-Hosted (Open Source) | Managed Hosting (SaaS) |
|---------|---------------------------|------------------------|
| **Cost** | Free (infrastructure costs only) | Subscription-based pricing |
| **Setup Time** | Days to weeks | Minutes to hours |
| **Security Updates** | Manual application required | Automatic, zero-downtime |
| **Monitoring** | Self-configured | Built-in, enterprise-grade |
| **Compliance** | Self-certification | Pre-certified (SOC 2, ISO 27001) |
| **Support** | Community forums | 24/7 enterprise support |
| **Scaling** | Manual capacity planning | Auto-scaling with load |
| **Disaster Recovery** | Self-managed backups | Automated, multi-region |
| **Uptime SLA** | No guarantee | 99.99% with financial credits |
| **Expertise Required** | High (DevOps, security, Aethel) | Low (managed by DIOTEC 360) |

### When to Choose Self-Hosted

- **Development & Testing**: Experimenting with Aethel or building proofs of concept
- **Full Control**: Need complete control over infrastructure and configuration
- **Cost Optimization**: Have existing infrastructure and DevOps expertise
- **Custom Requirements**: Require deep customization beyond managed service capabilities
- **Learning**: Want to understand Aethel internals deeply

### When to Choose Managed Hosting

- **Production Deployments**: Mission-critical financial applications
- **Rapid Time-to-Market**: Need to launch quickly without infrastructure setup
- **Compliance Requirements**: Must meet SOC 2, ISO 27001, or PCI DSS standards
- **Limited DevOps Resources**: Don't have dedicated infrastructure team
- **Enterprise Support**: Need guaranteed response times and expert assistance
- **Risk Mitigation**: Want DIOTEC 360 to handle security and reliability

## Pricing Philosophy

Our pricing model is designed to be transparent, predictable, and aligned with your success:

### Pricing Tiers

**Starter** - $2,500/month
- Up to 10,000 proofs/day
- Single region deployment
- 99.9% uptime SLA
- Email support (4-hour response)
- Community Slack access

**Professional** - $10,000/month
- Up to 100,000 proofs/day
- Multi-region deployment
- 99.95% uptime SLA
- 24/7 email & chat support (1-hour response)
- Dedicated Slack channel
- Monthly architecture reviews

**Enterprise** - Custom pricing
- Unlimited proofs
- Global multi-region deployment
- 99.99% uptime SLA
- 24/7 phone, email & chat support (15-minute response)
- Dedicated customer success manager
- Custom SLA terms
- On-premises deployment options
- White-glove migration assistance

### What's Included

All tiers include:
- Automatic security updates
- Real-time monitoring dashboards
- Compliance reporting tools
- Automated backups and disaster recovery
- API access and SDKs
- Documentation and training materials

### Volume Discounts

- Annual commitment: 15% discount
- Multi-year contracts: Custom pricing
- Non-profit organizations: 50% discount
- Academic institutions: 75% discount

## Enterprise Contact

Ready to discuss managed hosting for your organization?

**Sales Team**  
Email: sales@diotec360.com  
Phone: +1 (555) AETHEL-1  
Schedule a demo: https://diotec360.com/demo

**Technical Consultation**  
Email: solutions@diotec360.com  
Book architecture review: https://diotec360.com/architecture-review

## Recommended Production Path

**For Production Financial Applications, We Strongly Recommend Managed Hosting**

While Aethel's open source core enables self-hosting, production financial systems require:

1. **Security Expertise**: Constant vigilance against evolving threats
2. **Operational Excellence**: 24/7 monitoring and incident response
3. **Compliance Burden**: Maintaining certifications and audit trails
4. **Performance Optimization**: Tuning for scale and reliability
5. **Disaster Recovery**: Multi-region redundancy and failover

Our managed service provides all of this out-of-the-box, allowing your team to focus on building financial applications rather than managing infrastructure.

### Migration Path

Start with self-hosted development, then migrate to managed hosting for production:

1. **Phase 1**: Develop and test on self-hosted Aethel
2. **Phase 2**: Deploy staging environment on managed hosting
3. **Phase 3**: Migrate production with zero-downtime cutover
4. **Phase 4**: Decommission self-hosted infrastructure

We provide white-glove migration assistance for Enterprise customers.

## Getting Started

### Self-Hosted Trial

Try Aethel open source first:
```bash
pip install aethel
aethel init my-project
aethel run examples/safe_banking.ae
```

See [Installation Guide](../getting-started/installation.md) for details.

### Managed Hosting Trial

Start a 30-day free trial of managed hosting:

1. Sign up at https://cloud.diotec360.com
2. Create your first Aethel instance (takes ~5 minutes)
3. Deploy example applications
4. Integrate with your systems via API

No credit card required for trial.

## Frequently Asked Questions

**Q: Can I migrate from self-hosted to managed hosting later?**  
A: Yes, we provide migration tools and support. Enterprise customers receive white-glove migration assistance.

**Q: What happens if I exceed my proof quota?**  
A: We'll notify you before you hit limits. You can upgrade your tier or purchase additional capacity.

**Q: Can I deploy in my own cloud account?**  
A: Enterprise customers can choose managed hosting in their own AWS/Azure/GCP accounts.

**Q: Do you support on-premises deployment?**  
A: Yes, Enterprise tier includes on-premises deployment with managed support.

**Q: What's your data retention policy?**  
A: Configurable per customer. Default is 90 days for logs, 7 years for audit trails.

**Q: Can I get a custom SLA?**  
A: Yes, Enterprise customers can negotiate custom SLA terms including 99.999% uptime.

## Next Steps

- [Compare Features: Open vs Commercial](feature-matrix.md)
- [Enterprise Support Tiers](enterprise-support.md)
- [Certification Program](certification.md)
- [Contact Sales](mailto:sales@diotec360.com)
