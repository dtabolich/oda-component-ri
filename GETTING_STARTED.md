# Getting Started with API Mocking on Kubernetes

## 🎯 What You Have

A complete, production-ready solution for API mocking on Kubernetes with:
- ✅ 2 ready-to-deploy Helm charts
- ✅ 10+ tool comparisons
- ✅ Comprehensive documentation
- ✅ Example configurations
- ✅ Testing scripts

## ⚡ Quick Start (Choose One)

### Option 1: Prism (Recommended for Most Users)

```bash
# Deploy in 30 seconds
cd /workspace/charts
helm install my-mock PrismMockServer

# Test it
kubectl port-forward svc/my-mock-prism 8080:80
curl http://localhost:8080/health
```

**Best for**: OpenAPI-first development, frontend teams, CI/CD

---

### Option 2: WireMock (For Complex Testing)

```bash
# Deploy WireMock
cd /workspace/charts
helm install my-mock WireMock

# Test it
kubectl port-forward svc/my-mock-wiremock 8080:8080
curl http://localhost:8080/__admin/mappings
```

**Best for**: Integration testing, stateful scenarios

---

### Option 3: Microcks (Enterprise)

```bash
# Add Helm repo and deploy
helm repo add microcks https://microcks.io/helm
helm install microcks microcks/microcks -n microcks --create-namespace

# Access UI
kubectl port-forward svc/microcks -n microcks 8080:8080
```

**Best for**: Multi-protocol (REST/gRPC/GraphQL), API catalog

---

## 📖 Documentation Roadmap

### 1️⃣ First: Choose Your Tool

Read: **`/workspace/charts/COMPARISON_SUMMARY.md`**

Quick decision tree to pick the right tool for your needs.

---

### 2️⃣ Second: Quick Setup

Read: **`/workspace/charts/PrismMockServer/QUICKSTART.md`**

5-minute setup guide with examples.

---

### 3️⃣ Third: Deploy Your API

Use examples in: **`/workspace/charts/PrismMockServer/examples/`**

Ready-to-use configurations for different scenarios.

---

### 4️⃣ Fourth: Production Deployment

Read: **`/workspace/charts/PrismMockServer/DEPLOYMENT_GUIDE.md`**

Comprehensive guide with:
- Dev/QA/Prod scenarios
- Security best practices
- Monitoring setup
- Troubleshooting

---

### 5️⃣ Fifth: Explore Alternatives

Read: **`/workspace/API_MOCKING_TOOLS_COMPARISON.md`**

Detailed comparison of 10+ tools with:
- Feature matrices
- Deployment examples
- Use case recommendations

---

## 📁 File Organization

```
/workspace/
│
├── 📄 GETTING_STARTED.md              ← YOU ARE HERE
├── 📄 README_API_MOCKING.md           ← Complete overview
├── 📄 PRISM_DEPLOYMENT_OVERVIEW.md    ← Prism deep dive
├── 📄 API_MOCKING_TOOLS_COMPARISON.md ← Tool comparison
│
└── charts/
    │
    ├── PrismMockServer/               🌟 PRODUCTION READY
    │   ├── 📄 Chart.yaml
    │   ├── 📄 values.yaml
    │   ├── 📄 README.md               ← Main docs
    │   ├── 📄 QUICKSTART.md           ← Start here!
    │   ├── 📄 DEPLOYMENT_GUIDE.md     ← Advanced
    │   ├── 🔧 test-deployment.sh      ← Test script
    │   ├── templates/                 ← K8s manifests
    │   │   ├── deployment.yaml
    │   │   ├── service.yaml
    │   │   ├── configmap.yaml
    │   │   ├── ingress.yaml
    │   │   └── NOTES.txt
    │   └── examples/                  ← Ready-to-use configs
    │       ├── petstore-values.yaml
    │       ├── custom-api-values.yaml
    │       ├── production-values.yaml
    │       └── nodeport-values.yaml
    │
    ├── WireMock/                      🌟 PRODUCTION READY
    │   ├── 📄 Chart.yaml
    │   ├── 📄 values.yaml
    │   ├── 📄 README.md
    │   └── templates/
    │       ├── deployment.yaml
    │       ├── service.yaml
    │       └── configmap-*.yaml
    │
    ├── Microcks-Setup/
    │   └── 📄 MICROCKS_DEPLOYMENT_GUIDE.md
    │
    └── 📄 COMPARISON_SUMMARY.md       ← Quick reference
```

---

## 🎬 3-Minute Demo

```bash
# 1. Deploy Prism with Petstore API
helm install demo /workspace/charts/PrismMockServer \
  -f /workspace/charts/PrismMockServer/examples/petstore-values.yaml

# 2. Wait for pod to be ready
kubectl wait --for=condition=ready pod -l app=demo-prism --timeout=60s

# 3. Access the API
kubectl port-forward svc/demo-prism 8080:80 &

# 4. Test endpoints
curl http://localhost:8080/pets
curl http://localhost:8080/pets/1

# 5. Clean up
helm uninstall demo
```

---

## 🔍 Tool Selection (30 seconds)

Answer these questions:

**Q1: Do you need multi-protocol support (gRPC, GraphQL)?**
- Yes → Use **Microcks**
- No → Continue

**Q2: Do you need complex stateful scenarios?**
- Yes → Use **WireMock**
- No → Continue

**Q3: Do you have OpenAPI specifications?**
- Yes → Use **Prism** ✅ (Recommended)
- No → Use **WireMock** or **JSON Server**

---

## 💡 Common Use Cases

### Use Case 1: Frontend Development
**Problem**: Backend API not ready  
**Solution**: Prism with OpenAPI spec  
**Deploy**: 
```bash
helm install backend-mock /workspace/charts/PrismMockServer \
  --set spec.url="https://your-repo.com/api-spec.yaml"
```

---

### Use Case 2: CI/CD Testing
**Problem**: Need predictable API responses  
**Solution**: Prism in test namespace  
**Deploy**: 
```bash
helm install test-mock /workspace/charts/PrismMockServer \
  -f /workspace/charts/PrismMockServer/examples/custom-api-values.yaml \
  -n ci-testing --create-namespace
```

---

### Use Case 3: Integration Testing
**Problem**: Need stateful user flows  
**Solution**: WireMock with scenarios  
**Deploy**: 
```bash
helm install integration-mock /workspace/charts/WireMock
```

---

### Use Case 4: API Catalog
**Problem**: Need centralized API management  
**Solution**: Microcks platform  
**Deploy**: 
```bash
helm repo add microcks https://microcks.io/helm
helm install microcks microcks/microcks -n microcks --create-namespace
```

---

## 🚀 Next Steps

### For Beginners:
1. ✅ Deploy Prism with default values (2 minutes)
2. ✅ Test with `curl` (1 minute)
3. ✅ Review QUICKSTART.md (5 minutes)
4. ✅ Try petstore example (3 minutes)

### For Intermediate Users:
1. ✅ Deploy with your own OpenAPI spec
2. ✅ Configure Ingress for external access
3. ✅ Run test-deployment.sh script
4. ✅ Review DEPLOYMENT_GUIDE.md

### For Advanced Users:
1. ✅ Compare all tools in API_MOCKING_TOOLS_COMPARISON.md
2. ✅ Deploy WireMock for complex scenarios
3. ✅ Evaluate Microcks for enterprise use
4. ✅ Implement GitOps workflows

---

## 📊 What's Available

| Component | Status | Location |
|-----------|--------|----------|
| Prism Helm Chart | ✅ Ready | `/workspace/charts/PrismMockServer/` |
| WireMock Helm Chart | ✅ Ready | `/workspace/charts/WireMock/` |
| Microcks Guide | ✅ Ready | `/workspace/charts/Microcks-Setup/` |
| Example Configs | ✅ 4 examples | `/workspace/charts/PrismMockServer/examples/` |
| Test Script | ✅ Ready | `/workspace/charts/PrismMockServer/test-deployment.sh` |
| Documentation | ✅ 85KB+ | Multiple files |
| Tool Comparison | ✅ 10+ tools | `API_MOCKING_TOOLS_COMPARISON.md` |

---

## 🎓 Learning Path

### Week 1: Basics
- [ ] Deploy Prism with default values
- [ ] Test with sample API
- [ ] Review documentation
- [ ] Try different service types

### Week 2: Customization
- [ ] Deploy with your OpenAPI spec
- [ ] Configure resources and replicas
- [ ] Set up Ingress
- [ ] Test from external network

### Week 3: Advanced
- [ ] Compare multiple tools
- [ ] Deploy WireMock
- [ ] Integrate with CI/CD
- [ ] Implement monitoring

### Month 1: Production
- [ ] Deploy to production namespace
- [ ] Configure security policies
- [ ] Set up backup/restore
- [ ] Document for team

---

## 🆘 Need Help?

### Quick Troubleshooting

**Pod not starting?**
```bash
kubectl describe pod -l app=my-mock-prism
kubectl logs -l app=my-mock-prism
```

**Service not accessible?**
```bash
kubectl get svc,endpoints -l app=my-mock-prism
```

**Invalid OpenAPI spec?**
- Validate at: https://editor.swagger.io/

**Need examples?**
- Check: `/workspace/charts/PrismMockServer/examples/`

---

## 📞 Resources

### Documentation
- 📖 Main README: `README_API_MOCKING.md`
- 🚀 Quick Start: `charts/PrismMockServer/QUICKSTART.md`
- 🔧 Deployment Guide: `charts/PrismMockServer/DEPLOYMENT_GUIDE.md`
- 📊 Tool Comparison: `API_MOCKING_TOOLS_COMPARISON.md`

### External Links
- [Prism Documentation](https://docs.stoplight.io/docs/prism)
- [WireMock Documentation](https://wiremock.org/docs/)
- [Microcks Documentation](https://microcks.io/documentation/)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)

---

## ✨ Key Features

### Prism Chart
- ✅ Full OpenAPI v2/v3 support
- ✅ Request/response validation
- ✅ Multiple spec sources (URL, ConfigMap, Inline)
- ✅ Security hardened
- ✅ Production ready
- ✅ 4 example configurations
- ✅ Automated test script

### WireMock Chart
- ✅ Advanced request matching
- ✅ Response templating
- ✅ Stateful scenarios
- ✅ ConfigMap-based configuration
- ✅ Admin API support

### Documentation
- ✅ 85KB+ comprehensive guides
- ✅ 10+ tool comparisons
- ✅ Deployment scenarios
- ✅ Best practices
- ✅ Security guidelines

---

## 🎯 Summary

**You have everything you need to deploy API mocking on Kubernetes!**

**Start with**: Prism for most use cases  
**Upgrade to**: WireMock for complex testing  
**Consider**: Microcks for enterprise needs  

**Time to first mock**: < 2 minutes  
**Production ready**: Yes  
**Documentation**: Complete  

---

## 🚦 Quick Commands

```bash
# Deploy Prism (simplest)
cd /workspace/charts && helm install mock PrismMockServer

# Deploy with custom API
helm install mock PrismMockServer -f my-values.yaml

# Deploy WireMock
helm install mock WireMock

# Test deployment
./PrismMockServer/test-deployment.sh mock default

# Access mock server
kubectl port-forward svc/mock-prism 8080:80

# View logs
kubectl logs -l app=mock-prism -f

# Uninstall
helm uninstall mock
```

---

## 🎉 You're Ready!

Pick a chart, deploy it, and start mocking! 🚀

**Recommended first step**: 
```bash
cd /workspace/charts
helm install my-first-mock PrismMockServer
kubectl port-forward svc/my-first-mock-prism 8080:80
curl http://localhost:8080/health
```

**Next**: Read `/workspace/charts/PrismMockServer/QUICKSTART.md`

---

**Happy Mocking!** 🎊
