import { eq, and, desc, sql } from 'drizzle-orm';
import { getDb } from './db';
import {
  tenants,
  deployments,
  featureFlags,
  amiMetrics,
  analyticsEvents,
  type Tenant,
  type InsertTenant,
  type Deployment,
  type InsertDeployment,
  type FeatureFlag,
  type InsertFeatureFlag,
  type AmiMetric,
  type InsertAmiMetric,
  type AnalyticsEvent,
  type InsertAnalyticsEvent,
} from '../drizzle/schema';

// ============================================================================
// TENANTS
// ============================================================================

export async function createTenant(tenant: InsertTenant): Promise<Tenant | null> {
  const db = await getDb();
  if (!db) return null;

  try {
    const result = await db.insert(tenants).values(tenant);
    const insertedId = Number(result[0].insertId);
    return await getTenantById(insertedId);
  } catch (error) {
    console.error('[TenantDB] Failed to create tenant:', error);
    throw error;
  }
}

export async function getTenantById(id: number): Promise<Tenant | null> {
  const db = await getDb();
  if (!db) return null;

  const result = await db.select().from(tenants).where(eq(tenants.id, id)).limit(1);
  return result[0] || null;
}

export async function getTenantByTenantId(tenantId: string): Promise<Tenant | null> {
  const db = await getDb();
  if (!db) return null;

  const result = await db.select().from(tenants).where(eq(tenants.tenantId, tenantId)).limit(1);
  return result[0] || null;
}

export async function getAllTenants(): Promise<Tenant[]> {
  const db = await getDb();
  if (!db) return [];

  return await db.select().from(tenants).orderBy(desc(tenants.createdAt));
}

export async function updateTenant(id: number, updates: Partial<InsertTenant>): Promise<Tenant | null> {
  const db = await getDb();
  if (!db) return null;

  try {
    await db.update(tenants).set(updates).where(eq(tenants.id, id));
    return await getTenantById(id);
  } catch (error) {
    console.error('[TenantDB] Failed to update tenant:', error);
    throw error;
  }
}

export async function deleteTenant(id: number): Promise<boolean> {
  const db = await getDb();
  if (!db) return false;

  try {
    await db.delete(tenants).where(eq(tenants.id, id));
    return true;
  } catch (error) {
    console.error('[TenantDB] Failed to delete tenant:', error);
    return false;
  }
}

// ============================================================================
// DEPLOYMENTS
// ============================================================================

export async function createDeployment(deployment: InsertDeployment): Promise<Deployment | null> {
  const db = await getDb();
  if (!db) return null;

  try {
    const result = await db.insert(deployments).values(deployment);
    const insertedId = Number(result[0].insertId);
    return await getDeploymentById(insertedId);
  } catch (error) {
    console.error('[TenantDB] Failed to create deployment:', error);
    throw error;
  }
}

export async function getDeploymentById(id: number): Promise<Deployment | null> {
  const db = await getDb();
  if (!db) return null;

  const result = await db.select().from(deployments).where(eq(deployments.id, id)).limit(1);
  return result[0] || null;
}

export async function getDeploymentsByTenantId(tenantId: string): Promise<Deployment[]> {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(deployments)
    .where(eq(deployments.tenantId, tenantId))
    .orderBy(desc(deployments.createdAt));
}

export async function getAllDeployments(): Promise<Deployment[]> {
  const db = await getDb();
  if (!db) return [];

  return await db.select().from(deployments).orderBy(desc(deployments.createdAt));
}

export async function updateDeployment(id: number, updates: Partial<InsertDeployment>): Promise<Deployment | null> {
  const db = await getDb();
  if (!db) return null;

  try {
    await db.update(deployments).set(updates).where(eq(deployments.id, id));
    return await getDeploymentById(id);
  } catch (error) {
    console.error('[TenantDB] Failed to update deployment:', error);
    throw error;
  }
}

export async function deleteDeployment(id: number): Promise<boolean> {
  const db = await getDb();
  if (!db) return false;

  try {
    await db.delete(deployments).where(eq(deployments.id, id));
    return true;
  } catch (error) {
    console.error('[TenantDB] Failed to delete deployment:', error);
    return false;
  }
}

// ============================================================================
// FEATURE FLAGS
// ============================================================================

export async function setFeatureFlag(flag: InsertFeatureFlag): Promise<FeatureFlag | null> {
  const db = await getDb();
  if (!db) return null;

  try {
    // Upsert: insert or update if exists
    await db
      .insert(featureFlags)
      .values(flag)
      .onDuplicateKeyUpdate({
        set: { enabled: flag.enabled },
      });

    // Fetch the result
    const result = await db
      .select()
      .from(featureFlags)
      .where(and(eq(featureFlags.tenantId, flag.tenantId), eq(featureFlags.flagKey, flag.flagKey)))
      .limit(1);

    return result[0] || null;
  } catch (error) {
    console.error('[TenantDB] Failed to set feature flag:', error);
    throw error;
  }
}

export async function getFeatureFlagsByTenantId(tenantId: string): Promise<FeatureFlag[]> {
  const db = await getDb();
  if (!db) return [];

  return await db.select().from(featureFlags).where(eq(featureFlags.tenantId, tenantId));
}

export async function deleteFeatureFlag(tenantId: string, flagKey: string): Promise<boolean> {
  const db = await getDb();
  if (!db) return false;

  try {
    await db.delete(featureFlags).where(and(eq(featureFlags.tenantId, tenantId), eq(featureFlags.flagKey, flagKey)));
    return true;
  } catch (error) {
    console.error('[TenantDB] Failed to delete feature flag:', error);
    return false;
  }
}

// ============================================================================
// AMI METRICS
// ============================================================================

export async function getAmiMetricsByTenantId(
  tenantId: string,
  limit: number = 100
): Promise<AmiMetric[]> {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(amiMetrics)
    .where(eq(amiMetrics.tenantId, tenantId))
    .orderBy(desc(amiMetrics.timestamp))
    .limit(limit);
}

export async function getAmiMetricsByDeploymentId(
  deploymentId: string,
  limit: number = 100
): Promise<AmiMetric[]> {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(amiMetrics)
    .where(eq(amiMetrics.deploymentId, deploymentId))
    .orderBy(desc(amiMetrics.timestamp))
    .limit(limit);
}

export async function getAmiMetricsAggregated(tenantId: string): Promise<{
  context: number;
  proactivity: number;
  seamlessness: number;
  adaptivity: number;
}> {
  const db = await getDb();
  if (!db) {
    return { context: 0, proactivity: 0, seamlessness: 0, adaptivity: 0 };
  }

  try {
    const result = await db
      .select({
        principle: amiMetrics.principle,
        avgValue: sql<number>`AVG(${amiMetrics.value})`,
      })
      .from(amiMetrics)
      .where(eq(amiMetrics.tenantId, tenantId))
      .groupBy(amiMetrics.principle);

    const aggregated = {
      context: 0,
      proactivity: 0,
      seamlessness: 0,
      adaptivity: 0,
    };

    result.forEach((row) => {
      aggregated[row.principle] = Math.round(Number(row.avgValue));
    });

    return aggregated;
  } catch (error) {
    console.error('[TenantDB] Failed to get aggregated AmI metrics:', error);
    return { context: 0, proactivity: 0, seamlessness: 0, adaptivity: 0 };
  }
}

// ============================================================================
// ANALYTICS EVENTS
// ============================================================================

export async function createAnalyticsEvent(event: InsertAnalyticsEvent): Promise<AnalyticsEvent | null> {
  const db = await getDb();
  if (!db) return null;

  try {
    const result = await db.insert(analyticsEvents).values(event);
    const insertedId = Number(result[0].insertId);
    
    const inserted = await db
      .select()
      .from(analyticsEvents)
      .where(eq(analyticsEvents.id, insertedId))
      .limit(1);
    
    return inserted[0] || null;
  } catch (error) {
    console.error('[TenantDB] Failed to create analytics event:', error);
    throw error;
  }
}

export async function getAnalyticsEventsByTenantId(
  tenantId: string,
  limit: number = 100
): Promise<AnalyticsEvent[]> {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(analyticsEvents)
    .where(eq(analyticsEvents.tenantId, tenantId))
    .orderBy(desc(analyticsEvents.timestamp))
    .limit(limit);
}

export async function getAnalyticsEventCount(tenantId: string): Promise<number> {
  const db = await getDb();
  if (!db) return 0;

  try {
    const result = await db
      .select({ count: sql<number>`COUNT(*)` })
      .from(analyticsEvents)
      .where(eq(analyticsEvents.tenantId, tenantId));

    return Number(result[0]?.count || 0);
  } catch (error) {
    console.error('[TenantDB] Failed to get analytics event count:', error);
    return 0;
  }
}
