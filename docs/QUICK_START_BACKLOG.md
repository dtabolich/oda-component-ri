# Quick Start: Backlog Setup

Fast-track guide to get your backlog organized in 30 minutes.

## Step 1: Create Area Paths (5 minutes)

1. Go to **Project Settings** → **Project configuration** → **Areas**
2. Click **New child**
3. Create these areas:

```
Product-Management-Platform
├── ProductCatalog
│   ├── Core-API
│   ├── Party-Role-API
│   ├── Promotion-API
│   └── Infrastructure
├── ProductInventory
│   ├── Inventory-API
│   └── Integration
├── Shared-Services
└── Platform
```

**Quick CLI Script:**
```bash
PROJECT="Product-Management-Platform"

# ProductCatalog areas
az boards area project create --name "ProductCatalog" --project "$PROJECT"
az boards area project create --name "ProductCatalog\\Core-API" --project "$PROJECT"
az boards area project create --name "ProductCatalog\\Party-Role-API" --project "$PROJECT"
az boards area project create --name "ProductCatalog\\Promotion-API" --project "$PROJECT"
az boards area project create --name "ProductCatalog\\Infrastructure" --project "$PROJECT"

# ProductInventory areas
az boards area project create --name "ProductInventory" --project "$PROJECT"
az boards area project create --name "ProductInventory\\Inventory-API" --project "$PROJECT"
az boards area project create --name "ProductInventory\\Integration" --project "$PROJECT"

# Shared areas
az boards area project create --name "Shared-Services" --project "$PROJECT"
az boards area project create --name "Platform" --project "$PROJECT"
```

## Step 2: Create Teams (5 minutes)

1. Go to **Project Settings** → **Teams**
2. Create these teams:

| Team Name | Area Path | Description |
|-----------|-----------|-------------|
| ProductCatalog Team | ProductCatalog | Main product development |
| ProductInventory Team | ProductInventory | Plugin development |
| Platform Team | Platform, Shared-Services | Infrastructure & shared services |

**For each team:**
- Click **New team**
- Enter team name
- Configure area path
- Add team members

## Step 3: Set Up Iterations (5 minutes)

1. Go to **Project Settings** → **Project configuration** → **Iterations**
2. Create structure:

```
Product-Management-Platform
├── 2025
│   └── Q1
│       ├── Sprint 1 (Jan 6-19, 2025)
│       ├── Sprint 2 (Jan 20-Feb 2, 2025)
│       ├── Sprint 3 (Feb 3-16, 2025)
│       ├── Sprint 4 (Feb 17-Mar 2, 2025)
│       ├── Sprint 5 (Mar 3-16, 2025)
│       └── Sprint 6 (Mar 17-30, 2025)
```

**For each team:**
- Go to **Team configuration** → **Iterations**
- Select all Q1 sprints
- Set current sprint

## Step 4: Create Work Item Templates (5 minutes)

### Feature Template

Create a Feature work item with this content:

```
Title: [Feature] {Feature Name}

Description:
## Overview
What are we building?

## User Benefit
Why is this valuable?

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Dependencies
- List any dependencies

## Technical Notes
- Key technical considerations

Area Path: [Select appropriate area]
Tags: [component-name, version-tag]
```

Save as template: Three dots → **Templates** → **Capture as template**

### User Story Template

```
Title: As a {user}, I want to {action}, so that {benefit}

Description:
## User Story
As a [role]
I want [capability]
So that [benefit]

## Acceptance Criteria
- [ ] Given [context], when [action], then [result]

## Definition of Done
- [ ] Code complete and reviewed
- [ ] Tests written (>80% coverage)
- [ ] Documentation updated
- [ ] Deployed to dev
- [ ] QA validated

Area Path: [Select appropriate area]
Story Points: [Estimate]
```

Save as template.

## Step 5: Create Essential Queries (5 minutes)

### Query 1: My Work
```
Work Item Type IN ('User Story', 'Task', 'Bug')
AND State NOT IN ('Closed', 'Removed')
AND Assigned To = @Me
```

### Query 2: ProductCatalog Backlog
```
Work Item Type IN ('Feature', 'User Story')
AND Area Path UNDER 'Product-Management-Platform\ProductCatalog'
AND State IN ('New', 'Active')
ORDER BY Priority ASC
```

### Query 3: ProductInventory Backlog
```
Work Item Type IN ('Feature', 'User Story')
AND Area Path UNDER 'Product-Management-Platform\ProductInventory'
AND State IN ('New', 'Active')
ORDER BY Priority ASC
```

### Query 4: Current Sprint - All Teams
```
Work Item Type IN ('User Story', 'Task')
AND Iteration Path = @CurrentIteration
```

**Save Queries:**
1. Go to **Boards** → **Queries**
2. **New query**
3. Enter query
4. **Save query** → **Shared Queries**

## Step 6: Set Up Basic Dashboard (5 minutes)

1. Go to **Overview** → **Dashboards**
2. **New dashboard**: "Product Overview"
3. Add widgets:
   - **Sprint Burndown** (ProductCatalog Team)
   - **Sprint Burndown** (ProductInventory Team)
   - **Velocity** (All teams)
   - **Work Items** (Query: Current Sprint)

## Done! 🎉

You now have a functional backlog structure. 

## Next Steps

1. **Populate Backlog**: Add your first Epics and Features
2. **Assign Work Items**: Set area paths and assign to teams
3. **Plan First Sprint**: Schedule sprint planning meeting
4. **Train Teams**: Share this documentation

## Quick Reference

### Area Paths
- **Main Product**: `ProductCatalog`
- **Plugins**: `ProductInventory`
- **Shared**: `Shared-Services`, `Platform`

### Tags to Use
- Component: `productcatalog`, `productinventory`
- Type: `api`, `backend`, `frontend`, `infrastructure`
- Release: `v1.2.0`, `v1.3.0`
- Special: `cross-component`, `technical-debt`, `breaking-change`

### Sprint Cadence
- **Duration**: 2 weeks
- **Planning**: Monday, Week 1
- **Review**: Friday, Week 2
- **Retro**: Friday, Week 2

## Common Actions

### Create a Feature
1. **Boards** → **Backlogs**
2. **New Work Item** → **Feature**
3. Use template
4. Set Area Path (ProductCatalog or ProductInventory)
5. Add tags
6. Save

### Plan Sprint
1. **Boards** → **Backlogs**
2. Select team backlog
3. Drag items to current sprint
4. Check capacity
5. Commit to sprint

### Track Dependencies
1. Open work item
2. **Add link** → **Existing item**
3. Link type: **Predecessor/Successor**
4. Select dependent item
5. Add tag: `cross-component`

## Troubleshooting

**Can't see work items?**
- Check area path filters
- Verify team membership
- Check query filters

**Work items in wrong area?**
- Bulk select items
- Edit → Area Path
- Update to correct area

**Need help?**
- See full guide: [BACKLOG_MANAGEMENT_GUIDE.md](./BACKLOG_MANAGEMENT_GUIDE.md)
- Contact: backlog-admin@yourcompany.com

---

*Quick Start Guide - December 2025*
