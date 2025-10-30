# Dashboard Data Fixes - Complete

## Overview

Fixed incorrect workload calculations in WorkloadDashboardPage and replaced mocked data with real API data in IndexPage.

## Changes Made

### 1. Backend Changes

#### `backend/app/models/team_member.py`

- **Added** `max_story_points` field (Integer, default 40) to store each member's capacity
- **Updated** `to_dict()` method to include:
  - `maxStoryPoints` - member's max capacity
  - `totalStoryPoints` - current incomplete story points

#### `backend/app/routes/teams.py`

- **Enhanced** `calculate_member_metrics()` function to:
  - Return `total_story_points` (sum of incomplete tasks)
  - Use member's individual `max_story_points` for workload calculation
  - Calculate workload as: `(total_story_points / max_story_points) * 100`
- **Updated** all API endpoints to return new fields:
  - GET `/teams` - returns all members with workload data
  - GET `/teams/<id>` - returns single member with workload data
  - POST `/teams` - accepts and stores `maxStoryPoints`
  - PUT `/teams/<id>` - accepts updates to `maxStoryPoints`

#### `backend/migrations/add_max_story_points.py`

- **Created** migration script to add `max_story_points` column to existing database
- Includes both `upgrade()` and `downgrade()` functions
- Safe to run multiple times (checks if column exists)

### 2. Frontend Changes

#### `src/stores/team-store.ts`

- **Added** `totalStoryPoints?: number` to `TeamMember` interface
- **Added** `maxStoryPoints?: number` to `TeamMember` interface

#### `src/pages/WorkloadDashboardPage.vue`

- **Fixed** workload calculation to use backend-provided data
- **Changed** `membersWithWorkload` computed property to:
  - Use `member.workload` from API (instead of recalculating)
  - Use `member.totalStoryPoints` from API
  - Use `member.maxStoryPoints` from API (default 40)
- **Updated** project breakdown to show incomplete tasks (matching backend logic)
- **Fixed** task list to show all assigned tasks (not just active sprint tasks)

#### `src/pages/IndexPage.vue`

- **Replaced** all hardcoded project statistics with real data:
  - Total Projects → `projectStore.projects.length`
  - Projects On Track → count of projects with status "On Track"
  - Average Progress → calculated from actual project progress
  - Team Members → `teamStore.teamMembers.length`
  - Average Workload → calculated from team members' workload
  - Total Tasks → sum of tasks across all projects
  - Completed Tasks → sum of completed tasks across all projects
- **Replaced** active projects list with real data from `projectStore`
- **Added** computed properties for all statistics
- **Added** data fetching in `onMounted()` hook
- **Kept** PERT+RACI research metrics (demo/research data)
- **Kept** recent experiments list (no backend endpoint exists)

## Problem Resolution

### Problem 1: Workload Dashboard Showing Incorrect Data

**Root Cause:** Backend calculated workload from ALL incomplete tasks, but frontend recalculated using only active sprint tasks, causing mismatches.

**Solution:** Frontend now uses backend-provided workload and story points directly, ensuring consistency.

### Problem 2: Index Page Showing Mocked Data

**Root Cause:** All statistics were hardcoded arrays with fake data.

**Solution:** Replaced with computed properties that calculate real statistics from project and team stores.

## Database Migration

To apply the database changes, run:

```bash
cd backend
python migrations/add_max_story_points.py
```

Or manually add the column:

```sql
ALTER TABLE team_members ADD COLUMN max_story_points INTEGER NOT NULL DEFAULT 40;
```

## Testing Checklist

- [ ] Verify WorkloadDashboardPage shows correct workload percentages
- [ ] Verify workload matches between Team page and Workload Dashboard
- [ ] Verify IndexPage shows real project counts
- [ ] Verify IndexPage shows real team member counts
- [ ] Verify IndexPage active projects list is populated from database
- [ ] Verify no "undefined" or "NaN" values in dashboards
- [ ] Test with members who have no tasks (should show 0% workload)
- [ ] Test with members who have tasks in backlog (should count in workload)

## API Changes

### Team Member Response Format (NEW)

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "Frontend Developer",
  "systemRole": "developer",
  "avatar": "https://...",
  "status": "online",
  "activeProjects": 2,
  "workload": 75,
  "totalStoryPoints": 30,
  "maxStoryPoints": 40,
  "skills": ["React", "TypeScript"]
}
```

### New Fields

- `totalStoryPoints` (number) - Sum of story points from incomplete tasks
- `maxStoryPoints` (number) - Member's capacity per sprint (default: 40)

## Notes

- PERT+RACI research metrics remain as demo data (no backend source)
- Recent experiments list remains as demo data (no backend endpoint)
- All other dashboard metrics now use real data from API
- Workload calculation is now consistent across all pages
