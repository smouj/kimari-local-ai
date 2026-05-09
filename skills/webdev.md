# Skill: Web Development

## Objective
This skill enables Kimari to assist with modern web development tasks including React/Next.js applications, API design and implementation, database operations, and deployment strategies. It covers frontend components, backend services, full-stack patterns, and production deployment.

## Response Style
- Use modern framework patterns (React hooks, Next.js App Router, server components)
- Always separate concerns: presentational logic from business logic
- Include proper TypeScript types for all code examples
- Mention accessibility (a11y) considerations for UI components
- Reference current best practices and warn about deprecated approaches

## Good Response Examples

**Example 1: Next.js API route with error handling**
```typescript
// app/api/users/route.ts
import { NextResponse } from 'next/server';
import { z } from 'zod';

const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
});

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const validated = CreateUserSchema.parse(body);
    // ... save to database
    return NextResponse.json({ data: validated }, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', details: error.issues },
        { status: 400 }
      );
    }
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

**Example 2: React component with proper types and a11y**
```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({
  variant = 'primary', size = 'md',
  disabled, loading, children, onClick
}: ButtonProps) {
  const baseStyles = 'rounded-lg font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2';
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${/* size styles */}`}
      disabled={disabled || loading}
      onClick={onClick}
      aria-busy={loading}
    >
      {loading ? <Spinner size={size} /> : children}
    </button>
  );
}
```

**Example 3: Database query with Prisma**
```typescript
// Get paginated products with filters
async function getProducts(params: {
  page: number;
  perPage: number;
  category?: string;
  minPrice?: number;
  search?: string;
}) {
  const { page, perPage, category, minPrice, search } = params;
  const where = {
    ...(category && { category: { slug: category } }),
    ...(minPrice && { price: { gte: minPrice } }),
    ...(search && {
      OR: [
        { name: { contains: search, mode: 'insensitive' } },
        { description: { contains: search, mode: 'insensitive' } },
      ],
    }),
  };

  const [items, total] = await Promise.all([
    prisma.product.findMany({
      where, skip: (page - 1) * perPage, take: perPage,
      orderBy: { createdAt: 'desc' },
    }),
    prisma.product.count({ where }),
  ]);

  return { items, pagination: { page, perPage, total, totalPages: Math.ceil(total / perPage) } };
}
```

## Prohibited Behaviors
- Never use `any` type in TypeScript without explicitly acknowledging the trade-off
- Never write React components without considering accessibility (alt text, aria attributes, keyboard nav)
- Never recommend class components or legacy lifecycle methods for new code
- Never skip error handling in API routes or database operations
- Never suggest CSS-in-JS solutions for simple styling that Tailwind handles better

## Evaluation Tests
Build a Next.js 14 dashboard page with server-side data fetching, filtering, and pagination
Create a React form component with Zod validation, error display, and submission handling
Design a REST API for a blog platform with proper endpoint structure and status codes
Implement authentication using NextAuth.js with Google and GitHub providers
Write a Prisma schema for a multi-tenant SaaS application with proper relations and indexes
