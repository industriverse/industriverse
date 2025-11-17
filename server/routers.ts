import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import { z } from "zod";
import * as tenantDb from "./tenantDb";

export const appRouter = router({
    // if you need to use socket.io, read and register route in server/_core/index.ts, all api should start with '/api/' so that the gateway can route correctly
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  // Tenants API
  tenants: router({
    list: protectedProcedure.query(async () => {
      return await tenantDb.getAllTenants();
    }),
    
    getById: protectedProcedure
      .input(z.object({ id: z.number() }))
      .query(async ({ input }) => {
        return await tenantDb.getTenantById(input.id);
      }),
    
    getByTenantId: protectedProcedure
      .input(z.object({ tenantId: z.string() }))
      .query(async ({ input }) => {
        return await tenantDb.getTenantByTenantId(input.tenantId);
      }),
    
    create: protectedProcedure
      .input(z.object({
        tenantId: z.string(),
        name: z.string(),
        email: z.string().email(),
        contactPerson: z.string(),
        theme: z.string().optional(),
        customDomain: z.string().optional(),
        sslEnabled: z.number().optional(),
      }))
      .mutation(async ({ input }) => {
        return await tenantDb.createTenant(input);
      }),
    
    update: protectedProcedure
      .input(z.object({
        id: z.number(),
        name: z.string().optional(),
        email: z.string().email().optional(),
        contactPerson: z.string().optional(),
        theme: z.string().optional(),
        customDomain: z.string().optional(),
        sslEnabled: z.number().optional(),
        status: z.enum(["active", "suspended", "trial"]).optional(),
      }))
      .mutation(async ({ input }) => {
        const { id, ...updates } = input;
        return await tenantDb.updateTenant(id, updates);
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        return await tenantDb.deleteTenant(input.id);
      }),
  }),

  // Deployments API
  deployments: router({
    list: protectedProcedure.query(async () => {
      return await tenantDb.getAllDeployments();
    }),
    
    getByTenantId: protectedProcedure
      .input(z.object({ tenantId: z.string() }))
      .query(async ({ input }) => {
        return await tenantDb.getDeploymentsByTenantId(input.tenantId);
      }),
    
    create: protectedProcedure
      .input(z.object({
        tenantId: z.string(),
        deploymentId: z.string(),
        name: z.string(),
        enabledWidgets: z.string(), // JSON array
      }))
      .mutation(async ({ input }) => {
        return await tenantDb.createDeployment(input);
      }),
    
    update: protectedProcedure
      .input(z.object({
        id: z.number(),
        name: z.string().optional(),
        enabledWidgets: z.string().optional(),
        status: z.enum(["active", "inactive", "maintenance"]).optional(),
      }))
      .mutation(async ({ input }) => {
        const { id, ...updates } = input;
        return await tenantDb.updateDeployment(id, updates);
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        return await tenantDb.deleteDeployment(input.id);
      }),
  }),

  // Feature Flags API
  featureFlags: router({
    getByTenantId: protectedProcedure
      .input(z.object({ tenantId: z.string() }))
      .query(async ({ input }) => {
        return await tenantDb.getFeatureFlagsByTenantId(input.tenantId);
      }),
    
    set: protectedProcedure
      .input(z.object({
        tenantId: z.string(),
        flagKey: z.string(),
        enabled: z.number(),
      }))
      .mutation(async ({ input }) => {
        return await tenantDb.setFeatureFlag(input);
      }),
    
    delete: protectedProcedure
      .input(z.object({
        tenantId: z.string(),
        flagKey: z.string(),
      }))
      .mutation(async ({ input }) => {
        return await tenantDb.deleteFeatureFlag(input.tenantId, input.flagKey);
      }),
  }),

  // AmI Metrics API
  amiMetrics: router({
    getByTenantId: protectedProcedure
      .input(z.object({
        tenantId: z.string(),
        limit: z.number().optional(),
      }))
      .query(async ({ input }) => {
        return await tenantDb.getAmiMetricsByTenantId(input.tenantId, input.limit);
      }),
    
    getByDeploymentId: protectedProcedure
      .input(z.object({
        deploymentId: z.string(),
        limit: z.number().optional(),
      }))
      .query(async ({ input }) => {
        return await tenantDb.getAmiMetricsByDeploymentId(input.deploymentId, input.limit);
      }),
    
    getAggregated: protectedProcedure
      .input(z.object({ tenantId: z.string() }))
      .query(async ({ input }) => {
        return await tenantDb.getAmiMetricsAggregated(input.tenantId);
      }),
  }),

  // Analytics Events API
  analytics: router({
    create: protectedProcedure
      .input(z.object({
        tenantId: z.string(),
        deploymentId: z.string().optional(),
        eventType: z.string(),
        eventData: z.string().optional(),
        userId: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        return await tenantDb.createAnalyticsEvent(input);
      }),
    
    getByTenantId: protectedProcedure
      .input(z.object({
        tenantId: z.string(),
        limit: z.number().optional(),
      }))
      .query(async ({ input }) => {
        return await tenantDb.getAnalyticsEventsByTenantId(input.tenantId, input.limit);
      }),
    
    getCount: protectedProcedure
      .input(z.object({ tenantId: z.string() }))
      .query(async ({ input }) => {
        return await tenantDb.getAnalyticsEventCount(input.tenantId);
      }),
  }),
});

export type AppRouter = typeof appRouter;
