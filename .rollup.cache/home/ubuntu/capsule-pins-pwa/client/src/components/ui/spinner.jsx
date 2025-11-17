import { __rest } from "tslib";
import { Loader2Icon } from "lucide-react";
import { cn } from "@/lib/utils";
function Spinner(_a) {
    var className = _a.className, props = __rest(_a, ["className"]);
    return (<Loader2Icon role="status" aria-label="Loading" className={cn("size-4 animate-spin", className)} {...props}/>);
}
export { Spinner };
//# sourceMappingURL=spinner.jsx.map