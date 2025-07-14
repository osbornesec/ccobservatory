# Prime
Execute the following sections to understand the codebase then summarize your understanding.

## Run
git ls-files

## Run
find . -name "package.json" -o -name "Cargo.toml" -o -name "requirements.txt" -o -name "go.mod" -o -name "pyproject.toml" -o -name "composer.json" | head -10

## Run
find . -maxdepth 3 -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.cpp" -o -name "*.c" \) | head -20

## Run
find . -maxdepth 2 -type f \( -name "Dockerfile" -o -name "docker-compose.yml" -o -name "Makefile" -o -name "*.sh" -o -name "*.bat" \) | head -10

## Run
ls -la

## Run
find . -name ".github" -o -name ".gitlab" -o -name "scripts" -o -name "bin" -o -name "tests" -o -name "test" -o -name "__tests__" | head -10

## Read
README.md

## Read
.gitignore

## Read
CLAUDE.md

## Read
README.md

## Glob
**/package.json

## Glob
**/*.toml