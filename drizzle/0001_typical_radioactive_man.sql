CREATE TABLE `ami_metrics` (
	`id` int AUTO_INCREMENT NOT NULL,
	`tenantId` varchar(64) NOT NULL,
	`deploymentId` varchar(64) NOT NULL,
	`principle` enum('context','proactivity','seamlessness','adaptivity') NOT NULL,
	`value` int NOT NULL,
	`timestamp` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `ami_metrics_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `analytics_events` (
	`id` int AUTO_INCREMENT NOT NULL,
	`tenantId` varchar(64) NOT NULL,
	`deploymentId` varchar(64),
	`eventType` varchar(128) NOT NULL,
	`eventData` text,
	`userId` varchar(64),
	`timestamp` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `analytics_events_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `deployments` (
	`id` int AUTO_INCREMENT NOT NULL,
	`tenantId` varchar(64) NOT NULL,
	`deploymentId` varchar(64) NOT NULL,
	`name` varchar(255) NOT NULL,
	`enabledWidgets` text NOT NULL,
	`status` enum('active','inactive','maintenance') NOT NULL DEFAULT 'active',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `deployments_id` PRIMARY KEY(`id`),
	CONSTRAINT `deployments_deploymentId_unique` UNIQUE(`deploymentId`)
);
--> statement-breakpoint
CREATE TABLE `feature_flags` (
	`id` int AUTO_INCREMENT NOT NULL,
	`tenantId` varchar(64) NOT NULL,
	`flagKey` varchar(128) NOT NULL,
	`enabled` int NOT NULL DEFAULT 1,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `feature_flags_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `tenants` (
	`id` int AUTO_INCREMENT NOT NULL,
	`tenantId` varchar(64) NOT NULL,
	`name` varchar(255) NOT NULL,
	`email` varchar(320) NOT NULL,
	`contactPerson` varchar(255) NOT NULL,
	`theme` varchar(64) NOT NULL DEFAULT 'cosmic',
	`customDomain` varchar(255),
	`sslEnabled` int NOT NULL DEFAULT 1,
	`status` enum('active','suspended','trial') NOT NULL DEFAULT 'trial',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `tenants_id` PRIMARY KEY(`id`),
	CONSTRAINT `tenants_tenantId_unique` UNIQUE(`tenantId`)
);
