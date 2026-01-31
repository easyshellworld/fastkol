import * as React from "react"
import { cn } from "../../lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'secondary' | 'outline' | 'success'; // added success
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
    return (
        <div
            className={cn(
                "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                {
                    'border-transparent bg-slate-900 text-slate-50 hover:bg-slate-900/80': variant === 'default',
                    'border-transparent bg-green-600 text-white hover:bg-green-700': variant === 'success',
                },
                className
            )}
            {...props}
        />
    )
}

export { Badge }
