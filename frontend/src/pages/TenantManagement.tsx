import { useState } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { ArrowLeft, Plus, Pencil, Trash2, Search, RefreshCw } from "lucide-react";

export default function TenantManagement() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTenant, setSelectedTenant] = useState<any>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  // Queries
  const { data: tenants, isLoading, refetch } = trpc.tenants.list.useQuery();

  // Mutations
  const deleteMutation = trpc.tenants.delete.useMutation({
    onSuccess: () => {
      toast.success("Tenant deleted successfully");
      refetch();
      setIsDeleteDialogOpen(false);
    },
    onError: (error) => {
      toast.error(`Failed to delete tenant: ${error.message}`);
    },
  });

  const updateMutation = trpc.tenants.update.useMutation({
    onSuccess: () => {
      toast.success("Tenant updated successfully");
      refetch();
      setIsEditDialogOpen(false);
    },
    onError: (error) => {
      toast.error(`Failed to update tenant: ${error.message}`);
    },
  });

  // Filter tenants by search query
  const filteredTenants = tenants?.filter((tenant) =>
    tenant.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tenant.tenantId.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tenant.email?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDelete = () => {
    if (selectedTenant) {
      deleteMutation.mutate({ id: selectedTenant.id });
    }
  };

  const handleEdit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (selectedTenant) {
      const formData = new FormData(e.currentTarget);
      updateMutation.mutate({
        id: selectedTenant.id,
        name: formData.get("name") as string,
        email: formData.get("email") as string,
        status: formData.get("status") as string,
      });
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Link href="/admin">
              <Button variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Admin
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold">Tenant Management</h1>
              <p className="text-muted-foreground mt-1">
                Manage white-label deployments and configurations
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Link href="/admin/deploy">
              <Button size="sm">
                <Plus className="w-4 h-4 mr-2" />
                New Deployment
              </Button>
            </Link>
          </div>
        </div>

        {/* Search */}
        <Card className="p-4 mb-6">
          <div className="flex items-center gap-2">
            <Search className="w-5 h-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search by name, tenant ID, or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1"
            />
          </div>
        </Card>

        {/* Tenants Table */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">
              All Tenants ({filteredTenants?.length || 0})
            </h2>
            {isLoading ? (
              <div className="text-center py-12 text-muted-foreground">
                Loading tenants...
              </div>
            ) : filteredTenants && filteredTenants.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Tenant ID</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Industry</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Domain</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTenants.map((tenant) => (
                    <TableRow key={tenant.id}>
                      <TableCell className="font-medium">{tenant.name}</TableCell>
                      <TableCell>
                        <code className="text-xs bg-muted px-2 py-1 rounded">
                          {tenant.tenantId}
                        </code>
                      </TableCell>
                      <TableCell>{tenant.email || "—"}</TableCell>
                      <TableCell>{tenant.industry || "—"}</TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            tenant.status === "active"
                              ? "bg-green-500/10 text-green-500"
                              : tenant.status === "pending"
                              ? "bg-yellow-500/10 text-yellow-500"
                              : "bg-red-500/10 text-red-500"
                          }`}
                        >
                          {tenant.status}
                        </span>
                      </TableCell>
                      <TableCell>
                        {tenant.customDomain ? (
                          <a
                            href={`https://${tenant.customDomain}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline"
                          >
                            {tenant.customDomain}
                          </a>
                        ) : (
                          <span className="text-muted-foreground">
                            {tenant.tenantId}.industriverse.io
                          </span>
                        )}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(tenant.createdAt).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedTenant(tenant);
                              setIsEditDialogOpen(true);
                            }}
                          >
                            <Pencil className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedTenant(tenant);
                              setIsDeleteDialogOpen(true);
                            }}
                          >
                            <Trash2 className="w-4 h-4 text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground mb-4">
                  {searchQuery ? "No tenants match your search" : "No tenants yet"}
                </p>
                <Link href="/admin/deploy">
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Create First Tenant
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </Card>

        {/* Delete Confirmation Dialog */}
        <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Tenant</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete <strong>{selectedTenant?.name}</strong>?
                This action cannot be undone and will delete all associated deployments and data.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsDeleteDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? "Deleting..." : "Delete Tenant"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Edit Dialog */}
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Tenant</DialogTitle>
              <DialogDescription>
                Update tenant information
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleEdit}>
              <div className="space-y-4 py-4">
                <div>
                  <label className="text-sm font-medium">Name</label>
                  <Input
                    name="name"
                    defaultValue={selectedTenant?.name}
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <Input
                    name="email"
                    type="email"
                    defaultValue={selectedTenant?.email}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Status</label>
                  <select
                    name="status"
                    defaultValue={selectedTenant?.status}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value="active">Active</option>
                    <option value="pending">Pending</option>
                    <option value="suspended">Suspended</option>
                  </select>
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsEditDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={updateMutation.isPending}>
                  {updateMutation.isPending ? "Saving..." : "Save Changes"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
