# CI/CD Implementation for Eneo

## Overview
Implement a complete CI/CD pipeline for the Eneo project with automated Docker image building, versioning, and deployment triggers.

## 1. Create Branch Structure

### Create develop branch from main
```bash
git checkout main
git pull origin main
git checkout -b develop
git push origin develop
```

### Set branch protection rules on GitHub
- Go to Settings → Branches
- Add rule for `main`:
  - Require pull request reviews (at least 1)
  - Dismiss stale pull request approvals
  - Require branches to be up to date
- Add rule for `develop`:
  - Require pull request reviews (optional, can be 0 for speed)

## 2. Update GitHub Actions Workflows

### Create `.github/workflows/build-develop.yml`
This workflow builds and pushes Docker images when code is pushed to develop branch.

```yaml
name: Build and Push Development Images

on:
  push:
    branches:
      - develop
  pull_request:
    branches:
      - develop
    types: [closed]

env:
  REGISTRY: ghcr.io
  BACKEND_IMAGE_NAME: eneo-ai/eneo-backend
  FRONTEND_IMAGE_NAME: eneo-ai/eneo-frontend

jobs:
  build-and-push-develop:
    if: github.event_name == 'push' || (github.event_name == 'pull_request' && github.event.pull_request.merged == true)
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to the Container registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata for backend
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE_NAME }}
          tags: |
            type=raw,value=develop
            type=sha,prefix=develop-,format=short
          
      - name: Build and push backend Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          file: ./backend/Dockerfile
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}
          
      - name: Extract metadata for frontend
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE_NAME }}
          tags: |
            type=raw,value=develop
            type=sha,prefix=develop-,format=short
          
      - name: Build and push frontend Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          file: ./frontend/Dockerfile
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
```

### Update `.github/workflows/build_and_push_images.yml`
Rename and update the existing workflow for production builds.

```yaml
name: Build and Push Production Images

on:
  push:
    branches:
      - main
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  BACKEND_IMAGE_NAME: eneo-ai/eneo-backend
  FRONTEND_IMAGE_NAME: eneo-ai/eneo-frontend

jobs:
  build-and-push-production:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      attestations: write
      id-token: write
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to the Container registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      # Determine version tag
      - name: Get version
        id: version
        run: |
          if [[ "${{ github.event_name }}" == "release" ]]; then
            VERSION=${{ github.event.release.tag_name }}
          elif [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            # Get latest tag or default to v0.1.0
            LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
            # Extract version numbers
            VERSION_PARTS=(${LATEST_TAG//v/})
            VERSION_PARTS=(${VERSION_PARTS//./ })
            PATCH=$((${VERSION_PARTS[2]} + 1))
            VERSION="v${VERSION_PARTS[0]}.${VERSION_PARTS[1]}.$PATCH"
          fi
          echo "VERSION=$VERSION" >> $GITHUB_OUTPUT
          echo "Building version: $VERSION"
      
      # Backend
      - name: Extract backend metadata
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE_NAME }}
          tags: |
            type=raw,value=latest
            type=raw,value=${{ steps.version.outputs.VERSION }}
            type=sha,prefix={{branch}}-,format=short
          
      - name: Build and push backend Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          file: ./backend/Dockerfile
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}
          
      # Frontend
      - name: Extract frontend metadata
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE_NAME }}
          tags: |
            type=raw,value=latest
            type=raw,value=${{ steps.version.outputs.VERSION }}
            type=sha,prefix={{branch}}-,format=short
          
      - name: Build and push frontend Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          file: ./frontend/Dockerfile
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
      
      # Create git tag if building from main (not release)
      - name: Create git tag
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git tag ${{ steps.version.outputs.VERSION }}
          git push origin ${{ steps.version.outputs.VERSION }}
```

### Update `.github/workflows/pr-lint.yml`
Enhance the PR workflow to include branch naming validation.

```yaml
name: Pull Request Checks

on:
  pull_request:
    branches:
      - main
      - develop
    types:
      - opened
      - edited
      - synchronize
      - reopened

permissions:
  pull-requests: read

jobs:
  validate-pr:
    runs-on: ubuntu-latest
    name: Validate PR title and branch
    steps:
      - name: Validate semantic PR title
        uses: amannn/action-semantic-pull-request@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          types: |
            feat
            fix
            docs
            style
            refactor
            test
            chore
            perf
            ci
          requireScope: false
          subjectPattern: ^(?![A-Z]).+$
          subjectPatternError: |
            The subject "{subject}" found in the pull request title "{title}"
            didn't match the configured pattern. Please ensure that the subject
            doesn't start with an uppercase character.
      
      - name: Check branch naming
        run: |
          BRANCH_NAME="${{ github.head_ref }}"
          VALID_PREFIXES="^(feature|fix|hotfix|chore|docs|test|refactor)/"
          
          if [[ ! "$BRANCH_NAME" =~ $VALID_PREFIXES ]]; then
            echo "❌ Branch name '$BRANCH_NAME' does not follow naming convention."
            echo "Branch names should start with: feature/, fix/, hotfix/, chore/, docs/, test/, or refactor/"
            exit 1
          fi
          
          echo "✅ Branch name follows naming convention"

  frontend-checks:
    runs-on: ubuntu-latest
    name: Frontend typecheck, linting and formatting
    defaults:
      run:
        working-directory: frontend
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Install pnpm
        uses: pnpm/action-setup@v4
        with:
          version: latest
      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          cache-dependency-path: frontend/pnpm-lock.yaml 
          node-version: 20
          cache: pnpm
      - name: Install dependencies
        run: pnpm run setup:github
      - name: Run svelte-check
        run: pnpm run check
      - name: Run eslint
        run: pnpm run lint

  backend-checks:
    runs-on: ubuntu-latest
    name: Backend linting and tests
    defaults:
      run:
        working-directory: backend
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          virtualenvs-create: true
          virtualenvs-in-project: true
      - name: Install dependencies
        run: poetry install --no-interaction --no-root
      - name: Run linting
        run: |
          poetry run ruff check .
          poetry run black --check .
      - name: Run type checking
        run: poetry run mypy . || true  # Allow mypy to fail for now
```

## 3. Version Management Strategy

### Semantic Versioning
Use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Tagging Strategy
1. **Automatic patch version** on push to main
2. **Manual minor/major versions** via GitHub releases
3. **Development tags** include commit SHA for traceability

### Image Tags
- `latest` - Always points to the newest production release
- `v1.2.3` - Specific version tags for production
- `develop` - Latest development build
- `develop-abc123` - Development build with commit SHA

## 4. Feature Branch Workflow

### Creating a feature
```bash
# Start from develop
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Naming conventions
- `feature/` - New features
- `fix/` - Bug fixes  
- `hotfix/` - Urgent production fixes
- `chore/` - Maintenance tasks
- `docs/` - Documentation updates
- `test/` - Test additions/changes
- `refactor/` - Code refactoring

### Merging process
1. Create PR to `develop`
2. After review and testing, merge to `develop`
3. Automatic build and deploy to test environment
4. When ready for production, create PR from `develop` to `main`
5. Merge triggers production build with new version tag

## 5. Implementation Steps

1. **Create develop branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b develop
   git push -u origin develop
   ```

2. **Update GitHub settings**
   - Set default branch to `develop` for development
   - Configure branch protection rules
   - Set up required status checks

3. **Add workflow files**
   - Create/update the three workflow files above
   - Commit to a feature branch
   - Create PR to develop to test

4. **Test the pipeline**
   - Push to develop → Should build `:develop` images
   - Merge to main → Should build `:latest` and version tag
   - Create a release → Should build with release tag

5. **Update documentation**
   - Update README with branch strategy
   - Document the release process
   - Add CONTRIBUTING.md with branch naming conventions

## Expected Outcomes

After implementation:
- ✅ Automatic builds for both develop and main branches
- ✅ Proper version tagging on all images
- ✅ Clear separation between test and production
- ✅ Traceable builds with commit SHAs
- ✅ Protected branches preventing accidental pushes
- ✅ Standardized PR and branch naming

## Notes for Implementation

- The existing `build_and_push_images.yml` should be renamed or replaced
- Ensure all team members understand the new branch strategy
- Consider adding a webhook secret as a GitHub secret for future webhook integration
- The workflows use GitHub's built-in GITHUB_TOKEN, no additional secrets needed for public repos