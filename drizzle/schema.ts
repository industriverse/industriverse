import { int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * Tenants table - White-label client organizations
 */
export const tenants = mysqlTable("tenants", {
  id: int("id").autoincrement().primaryKey(),
  tenantId: varchar("tenantId", { length: 64 }).notNull().unique(),
  name: varchar("name", { length: 255 }).notNull(),
  email: varchar("email", { length: 320 }).notNull(),
  contactPerson: varchar("contactPerson", { length: 255 }).default(""),
  theme: text("theme"), // JSON theme configuration
  customDomain: varchar("customDomain", { length: 255 }),
  sslEnabled: int("sslEnabled").default(1).notNull(), // 1 = true, 0 = false
  status: mysqlEnum("status", ["active", "suspended", "trial"]).default("trial").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Tenant = typeof tenants.$inferSelect;
export type InsertTenant = typeof tenants.$inferInsert;

/**
 * Deployments table - Individual tenant deployments with widget configuration
 */
export const deployments = mysqlTable("deployments", {
  id: int("id").autoincrement().primaryKey(),
  tenantId: varchar("tenantId", { length: 64 }).notNull(),
  deploymentId: varchar("deploymentId", { length: 64 }).notNull().unique(),
  name: varchar("name", { length: 255 }).notNull(),
  enabledWidgets: text("enabledWidgets").notNull(), // JSON array of widget names
  status: mysqlEnum("status", ["active", "inactive", "maintenance"]).default("active").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Deployment = typeof deployments.$inferSelect;
export type InsertDeployment = typeof deployments.$inferInsert;

/**
 * Feature Flags table - Per-tenant feature configuration
 */
export const featureFlags = mysqlTable("feature_flags", {
  id: int("id").autoincrement().primaryKey(),
  tenantId: varchar("tenantId", { length: 64 }).notNull(),
  flagKey: varchar("flagKey", { length: 128 }).notNull(),
  enabled: int("enabled").default(1).notNull(), // 1 = true, 0 = false
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type FeatureFlag = typeof featureFlags.$inferSelect;
export type InsertFeatureFlag = typeof featureFlags.$inferInsert;

/**
 * AmI Metrics table - Real-time Ambient Intelligence principle measurements
 */
export const amiMetrics = mysqlTable("ami_metrics", {
  id: int("id").autoincrement().primaryKey(),
  tenantId: varchar("tenantId", { length: 64 }).notNull(),
  deploymentId: varchar("deploymentId", { length: 64 }).notNull(),
  principle: mysqlEnum("principle", ["context", "proactivity", "seamlessness", "adaptivity"]).notNull(),
  value: int("value").notNull(), // 0-100 percentage
  timestamp: timestamp("timestamp").defaultNow().notNull(),
});

export type AmiMetric = typeof amiMetrics.$inferSelect;
export type InsertAmiMetric = typeof amiMetrics.$inferInsert;

/**
 * Analytics Events table - User activity tracking
 */
export const analyticsEvents = mysqlTable("analytics_events", {
  id: int("id").autoincrement().primaryKey(),
  tenantId: varchar("tenantId", { length: 64 }).notNull(),
  deploymentId: varchar("deploymentId", { length: 64 }),
  eventType: varchar("eventType", { length: 128 }).notNull(),
  eventData: text("eventData"), // JSON object
  userId: varchar("userId", { length: 64 }),
  timestamp: timestamp("timestamp").defaultNow().notNull(),
});

export type AnalyticsEvent = typeof analyticsEvents.$inferSelect;
export type InsertAnalyticsEvent = typeof analyticsEvents.$inferInsert;