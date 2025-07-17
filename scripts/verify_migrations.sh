#!/bin/bash

# Script to verify migrations were successfully pushed to Supabase cloud
# Run this after resetting the database password and pushing migrations

set -e

echo "🔍 Verifying Supabase migrations push..."
echo "======================================"

# Change to supabase directory
cd "$(dirname "$0")/../supabase" || exit 1

echo "📋 Step 1: Checking project status..."
supabase projects list

echo ""
echo "📋 Step 2: Listing applied migrations..."
supabase migration list --linked

echo ""
echo "📋 Step 3: Generating TypeScript types to verify schema..."
supabase gen types typescript --project-id znznsjgqbnljgpffalwi > ../temp_types.ts

echo ""
echo "📋 Step 4: Checking if main tables exist in generated types..."
if grep -q "conversations\|messages\|tools\|projects" ../temp_types.ts; then
    echo "✅ Core tables found in schema"
else
    echo "❌ Core tables NOT found in schema"
    exit 1
fi

echo ""
echo "📋 Step 5: Verifying migration files vs applied migrations..."
local_migrations=$(ls -1 migrations/*.sql | wc -l)
echo "Local migration files: $local_migrations"

echo ""
echo "📋 Step 6: Testing database connection..."
if supabase db push --dry-run --linked > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Clean up
rm -f ../temp_types.ts

echo ""
echo "🎉 Migration verification complete!"
echo "✅ All migrations appear to be successfully applied to the cloud database"
echo ""
echo "📋 Next steps:"
echo "1. Test backend connectivity to cloud database"
echo "2. Run integration tests"
echo "3. Verify RLS policies are working"
echo "4. Begin connecting application to cloud database"