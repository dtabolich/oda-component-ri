# Deployment Runbook

Operational guide for deploying and managing the Product Management platform.

## Quick Reference

| Environment | URL | Namespace | Approvers | SLA |
|------------|-----|-----------|-----------|-----|
| Development | dev.yourdomain.com | dev-components | None | Best effort |
| Staging | staging.yourdomain.com | staging-components | QA Lead | 95% |
| Production | yourdomain.com | production-components | 2+ Approvers | 99.9% |

---

## Pre-Deployment Checklist

### Before Any Deployment

- [ ] Check current system status
- [ ] Verify all tests passing
- [ ] Review recent incidents
- [ ] Check monitoring dashboards
- [ ] Notify stakeholders
- [ ] Verify backup is recent
- [ ] Check maintenance window

### Production Deployment Specific

- [ ] Change request approved
- [ ] Rollback plan documented
- [ ] On-call team briefed
- [ ] Communication plan ready
- [ ] Monitoring alerts configured
- [ ] Load test completed (for major changes)
- [ ] Security scan passed

---

## Deployment Procedures

### Standard Deployment (via Pipeline)

#### Development Deployment

**Trigger**: Automatic on merge to `develop`

**Process**:
1. Code merged to `develop` branch
2. CI-Build pipeline validates code
3. Docker images built and pushed
4. Helm charts deployed automatically
5. Smoke tests run

**Validation**:
```bash
# Check deployment status
kubectl get deployments -n dev-components
kubectl get pods -n dev-components
kubectl get services -n dev-components

# Check logs
kubectl logs -n dev-components -l app=productcatalog --tail=50
```

**Rollback** (if needed):
```bash
helm rollback productcatalog-dev -n dev-components
```

---

#### Staging Deployment

**Trigger**: Automatic when release branch created

**Process**:
1. Create release branch: `release/X.Y.Z`
2. Pipeline triggers automatically
3. Deployment to dev first
4. Automatic deployment to staging
5. QA validation required
6. Integration tests run

**Validation**:
```bash
# Check all components
kubectl get all -n staging-components

# Run smoke tests
./scripts/smoke-test.sh staging

# Check metrics
kubectl top pods -n staging-components
```

**Rollback**:
```bash
helm rollback productcatalog-staging -n staging-components
helm rollback productinventory-staging -n staging-components
```

---

#### Production Deployment

**Trigger**: Manual approval after staging validation

**Process**:

**Step 1: Pre-Deployment (15 min before)**
```bash
# 1. Check current production state
kubectl get deployments -n production-components
helm list -n production-components

# 2. Create backup
kubectl get all -n production-components -o yaml > production-backup-$(date +%Y%m%d-%H%M%S).yaml

# 3. Check cluster health
kubectl get nodes
kubectl top nodes

# 4. Verify monitoring
# - Check Grafana dashboards
# - Verify alerting is working
# - Check error rates are normal
```

**Step 2: Deployment Approval**
1. Review deployment request in Azure DevOps
2. Verify all checks passed
3. Confirm rollback plan
4. Approve deployment

**Step 3: Monitor Deployment (Pipeline runs automatically)**
- Watch pipeline progress
- Monitor pod rollout status
- Check logs for errors
- Verify health checks passing

**Step 4: Post-Deployment Validation (30 minutes)**
```bash
# 1. Verify pods are running
kubectl get pods -n production-components

# 2. Check service endpoints
kubectl get services -n production-components

# 3. Run production smoke tests
./scripts/smoke-test.sh production

# 4. Check application logs
kubectl logs -n production-components -l app=productcatalog --tail=100 | grep -i error

# 5. Monitor metrics
# - Response times
# - Error rates
# - Request throughput
# - Resource utilization

# 6. Verify database connections
kubectl exec -it -n production-components <pod-name> -- mongo --eval "db.stats()"
```

**Step 5: Communication**
- Post deployment success message
- Update status page
- Notify stakeholders

---

### Hotfix Deployment

**When to Use**: Critical bugs, security issues, production outages

**Process**:

**Step 1: Create Hotfix Branch**
```bash
# From main branch
git checkout main
git pull
git checkout -b hotfix/critical-fix-description
```

**Step 2: Make Fix**
- Keep changes minimal
- Focus only on the critical issue
- Include tests

**Step 3: Fast-Track Pipeline**
```bash
# Push to trigger hotfix pipeline
git add .
git commit -m "Hotfix: Critical issue description"
git push origin hotfix/critical-fix-description
```

**Step 4: Expedited Review**
- Create PR with "Hotfix" label
- Get single approver (senior team member)
- Hotfix pipeline runs automatically

**Step 5: Staging Validation**
- Pipeline deploys to staging first
- Quick validation (15-30 minutes)
- Test specific fix

**Step 6: Production Deployment**
- Approve in Production-Hotfix environment
- Monitor closely during deployment
- Extended monitoring period (2 hours)

**Step 7: Post-Hotfix**
```bash
# Merge back to main
git checkout main
git merge hotfix/critical-fix-description
git push

# Merge to develop
git checkout develop
git merge hotfix/critical-fix-description
git push

# Tag the hotfix
git tag -a hotfix-X.Y.Z -m "Hotfix: Description"
git push --tags
```

**Step 8: Post-Mortem**
- Schedule post-mortem meeting
- Document root cause
- Create preventive action items

---

## Rollback Procedures

### Quick Rollback (Helm)

**When to Use**: Deployment issues, application errors, performance degradation

**Development:**
```bash
helm rollback productcatalog-dev -n dev-components
```

**Staging:**
```bash
helm rollback productcatalog-staging -n staging-components
```

**Production:**
```bash
# 1. Verify current revision
helm history productcatalog-prod -n production-components

# 2. Rollback to previous version
helm rollback productcatalog-prod -n production-components

# 3. Or rollback to specific revision
helm rollback productcatalog-prod 5 -n production-components

# 4. Verify rollback
kubectl get pods -n production-components
kubectl rollout status deployment/productcatalogapi -n production-components
```

### Image Tag Rollback

**When to Use**: Specific microservice issue

```bash
# Rollback specific deployment
kubectl set image deployment/productcatalogapi \
  productcatalogapi=yourregistry.azurecr.io/productcatalogapi:previous-version \
  -n production-components

# Verify rollback
kubectl rollout status deployment/productcatalogapi -n production-components
```

### Full Environment Rollback

**When to Use**: Multiple component issues, system-wide problems

```bash
# 1. Stop current deployment
kubectl rollout pause deployment/productcatalogapi -n production-components

# 2. Restore from backup
kubectl apply -f production-backup-TIMESTAMP.yaml

# 3. Verify restoration
kubectl get all -n production-components

# 4. Resume if needed
kubectl rollout resume deployment/productcatalogapi -n production-components
```

---

## Health Checks

### Application Health

```bash
# Check pod status
kubectl get pods -n <namespace>

# Check pod health
kubectl describe pod <pod-name> -n <namespace>

# Check logs
kubectl logs <pod-name> -n <namespace> --tail=100

# Check events
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n <namespace>
```

### Service Health

```bash
# Check services
kubectl get services -n <namespace>

# Check endpoints
kubectl get endpoints -n <namespace>

# Test service connectivity
kubectl run test-pod --rm -i --tty --image=curlimages/curl -- sh
curl http://service-name.namespace.svc.cluster.local/health
```

### Database Health

```bash
# MongoDB health check
kubectl exec -it <mongodb-pod> -n <namespace> -- mongo --eval "db.serverStatus()"

# Check connections
kubectl exec -it <mongodb-pod> -n <namespace> -- mongo --eval "db.serverStatus().connections"
```

---

## Common Issues and Solutions

### Issue: Pods in CrashLoopBackOff

**Diagnosis:**
```bash
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous
```

**Common Causes & Solutions:**
- **Config error**: Check ConfigMap/Secrets
- **Resource limits**: Increase limits in values file
- **Database unavailable**: Check MongoDB status
- **Image pull error**: Verify ACR credentials

### Issue: Service Unreachable

**Diagnosis:**
```bash
kubectl get services -n <namespace>
kubectl get endpoints -n <namespace>
kubectl describe service <service-name> -n <namespace>
```

**Solutions:**
- Verify pod labels match service selector
- Check pod readiness probes
- Verify network policies

### Issue: High Memory Usage

**Diagnosis:**
```bash
kubectl top pods -n <namespace>
kubectl describe pod <pod-name> -n <namespace>
```

**Solutions:**
- Restart pods: `kubectl rollout restart deployment/<deployment-name> -n <namespace>`
- Increase memory limits
- Check for memory leaks in logs

### Issue: Slow Response Times

**Diagnosis:**
- Check pod CPU/memory usage
- Check database performance
- Review application logs for slow queries

**Solutions:**
- Scale up: `kubectl scale deployment/<deployment-name> --replicas=5 -n <namespace>`
- Enable HPA if not already
- Optimize database queries

---

## Monitoring and Alerts

### Key Metrics to Monitor

**Application Metrics:**
- Request rate
- Error rate
- Response time (p50, p95, p99)
- Active connections
- Queue depth

**Infrastructure Metrics:**
- Pod CPU usage
- Pod memory usage
- Node resource utilization
- Disk usage
- Network throughput

**Database Metrics:**
- Connection count
- Query response time
- Replication lag
- Disk usage

### Alert Response

**Critical Alert**: Immediate action required
1. Acknowledge alert
2. Assess impact
3. Follow runbook
4. Escalate if needed
5. Page on-call engineer

**Warning Alert**: Action required within 24 hours
1. Acknowledge alert
2. Create tracking ticket
3. Schedule investigation
4. Monitor for escalation

---

## Maintenance Tasks

### Weekly Tasks

```bash
# Check pod restarts
kubectl get pods -n production-components --sort-by='.status.containerStatuses[0].restartCount'

# Review logs for errors
kubectl logs -n production-components -l app=productcatalog --since=7d | grep -i error

# Check disk usage
kubectl exec -it <pod-name> -n production-components -- df -h
```

### Monthly Tasks

- Review and update resource limits
- Audit access logs
- Update dependencies
- Review and prune old images
- Database maintenance
- Backup verification

### Quarterly Tasks

- Disaster recovery drill
- Security audit
- Performance testing
- Capacity planning
- Update runbooks

---

## Emergency Contacts

| Role | Primary | Backup | Contact |
|------|---------|---------|---------|
| On-Call Engineer | TBD | TBD | PagerDuty |
| DevOps Lead | TBD | TBD | Phone/Slack |
| Platform Lead | TBD | TBD | Phone/Slack |
| Security Team | TBD | TBD | Email |

---

## References

- [Azure DevOps Setup Guide](./AZURE_DEVOPS_SETUP_GUIDE.md)
- [Release Management Guide](./RELEASE_MANAGEMENT_GUIDE.md)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)

---

*Last Updated: December 2025*
