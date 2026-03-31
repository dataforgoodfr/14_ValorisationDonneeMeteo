### Exercise 1: Basic Pipeline Creation (40 min)
1. Create `.github/workflows/ci.yml` or `.gitlab-ci.yml`
2. Add stages:
   - Install dependencies
   - Run tests
   - Run linter
   - Run security scan
   - Build Docker image
   - Push to registry (on main branch only)

### Exercise 2: Pipeline Testing (15 min)
1. Intentionally break a test to verify CI catches it
2. Fix the test and verify pipeline passes
3. Add a CI badge to your README

**Deliverable**: Functional CI/CD pipeline with badge in README
- Docker image
- test report
- scan code report
- trivy report

