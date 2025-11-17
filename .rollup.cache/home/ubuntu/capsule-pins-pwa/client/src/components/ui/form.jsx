"use client";
import { __assign, __rest } from "tslib";
import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { Controller, FormProvider, useFormContext, useFormState, } from "react-hook-form";
import { cn } from "@/lib/utils";
import { Label } from "@/components/ui/label";
var Form = FormProvider;
var FormFieldContext = React.createContext({});
var FormField = function (_a) {
    var props = __rest(_a, []);
    return (<FormFieldContext.Provider value={{ name: props.name }}>
      <Controller {...props}/>
    </FormFieldContext.Provider>);
};
var useFormField = function () {
    var fieldContext = React.useContext(FormFieldContext);
    var itemContext = React.useContext(FormItemContext);
    var getFieldState = useFormContext().getFieldState;
    var formState = useFormState({ name: fieldContext.name });
    var fieldState = getFieldState(fieldContext.name, formState);
    if (!fieldContext) {
        throw new Error("useFormField should be used within <FormField>");
    }
    var id = itemContext.id;
    return __assign({ id: id, name: fieldContext.name, formItemId: "".concat(id, "-form-item"), formDescriptionId: "".concat(id, "-form-item-description"), formMessageId: "".concat(id, "-form-item-message") }, fieldState);
};
var FormItemContext = React.createContext({});
function FormItem(_a) {
    var className = _a.className, props = __rest(_a, ["className"]);
    var id = React.useId();
    return (<FormItemContext.Provider value={{ id: id }}>
      <div data-slot="form-item" className={cn("grid gap-2", className)} {...props}/>
    </FormItemContext.Provider>);
}
function FormLabel(_a) {
    var className = _a.className, props = __rest(_a, ["className"]);
    var _b = useFormField(), error = _b.error, formItemId = _b.formItemId;
    return (<Label data-slot="form-label" data-error={!!error} className={cn("data-[error=true]:text-destructive", className)} htmlFor={formItemId} {...props}/>);
}
function FormControl(_a) {
    var props = __rest(_a, []);
    var _b = useFormField(), error = _b.error, formItemId = _b.formItemId, formDescriptionId = _b.formDescriptionId, formMessageId = _b.formMessageId;
    return (<Slot data-slot="form-control" id={formItemId} aria-describedby={!error
            ? "".concat(formDescriptionId)
            : "".concat(formDescriptionId, " ").concat(formMessageId)} aria-invalid={!!error} {...props}/>);
}
function FormDescription(_a) {
    var className = _a.className, props = __rest(_a, ["className"]);
    var formDescriptionId = useFormField().formDescriptionId;
    return (<p data-slot="form-description" id={formDescriptionId} className={cn("text-muted-foreground text-sm", className)} {...props}/>);
}
function FormMessage(_a) {
    var _b;
    var className = _a.className, props = __rest(_a, ["className"]);
    var _c = useFormField(), error = _c.error, formMessageId = _c.formMessageId;
    var body = error ? String((_b = error === null || error === void 0 ? void 0 : error.message) !== null && _b !== void 0 ? _b : "") : props.children;
    if (!body) {
        return null;
    }
    return (<p data-slot="form-message" id={formMessageId} className={cn("text-destructive text-sm", className)} {...props}>
      {body}
    </p>);
}
export { useFormField, Form, FormItem, FormLabel, FormControl, FormDescription, FormMessage, FormField, };
//# sourceMappingURL=form.jsx.map