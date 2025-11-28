import { __awaiter, __generator } from "tslib";
import express from "express";
import { createServer } from "http";
import path from "path";
import { fileURLToPath } from "url";
var __filename = fileURLToPath(import.meta.url);
var __dirname = path.dirname(__filename);
function startServer() {
    return __awaiter(this, void 0, void 0, function () {
        var app, server, staticPath, port;
        return __generator(this, function (_a) {
            app = express();
            server = createServer(app);
            staticPath = process.env.NODE_ENV === "production"
                ? path.resolve(__dirname, "public")
                : path.resolve(__dirname, "..", "dist", "public");
            app.use(express.static(staticPath));
            // Handle client-side routing - serve index.html for all routes
            app.get("*", function (_req, res) {
                res.sendFile(path.join(staticPath, "index.html"));
            });
            port = process.env.PORT || 3000;
            server.listen(port, function () {
                console.log("Server running on http://localhost:".concat(port, "/"));
            });
            return [2 /*return*/];
        });
    });
}
startServer().catch(console.error);
//# sourceMappingURL=index.js.map