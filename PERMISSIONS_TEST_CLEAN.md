# CI/CD Permissions Test - Clean Version

## Test Purpose
**Primary Goal**: Test the complete workflow of adding a new feature to develop branch, then pushing it to main branch to verify versioning and tagging works correctly.

**Secondary Goal**: Verify that GitHub Actions can now create git tags after enabling "Read and write permissions".

## Test Scenario: Clean Feature Development
- **Feature**: Add permissions testing documentation (without secrets)
- **Branch**: `feature/permissions-test-clean`
- **Expected Version**: `v1.0.6` (next increment after v1.0.5)

## Complete Workflow Test

### Step 1: Feature Development
- ✅ Create clean feature branch from develop
- ✅ Add new feature (this test file)
- ✅ Push feature branch to GitHub (no secrets)

### Step 2: Develop Branch Integration
- ✅ Merge feature to develop
- ✅ Push develop → triggers develop build
- ✅ Build images with tags: `develop`, `develop-{sha}`
- ✅ No git tag creation (correct behavior)

### Step 3: Production Release  
- ✅ Merge develop to main
- ✅ Push main → triggers production build
- ✅ Build images with tags: `latest`, `v1.0.6`, `main-{sha}`
- ✅ **CREATE GIT TAG**: `v1.0.6` should be created in repository
- ✅ No permission errors

## Expected Results After Main Build:
```bash
# Check git tags
git pull origin main
git tag -l
# Should show: v1.0.0, v1.0.1, v1.0.2, v1.0.3, v1.0.4, v1.0.5, v1.0.6

# Check container images
docker pull ghcr.io/ccimen/eneo-testcicd-backend:latest
docker pull ghcr.io/ccimen/eneo-testcicd-backend:v1.0.6
docker pull ghcr.io/ccimen/eneo-testcicd-frontend:latest
docker pull ghcr.io/ccimen/eneo-testcicd-frontend:v1.0.6
```

## Permission Settings Applied:
- ✅ Repository Settings → Actions → General → Workflow permissions → "Read and write permissions"
- ✅ "Allow GitHub Actions to create and approve pull requests" enabled

---
**Status**: Testing permissions fix for git tag creation (clean version)