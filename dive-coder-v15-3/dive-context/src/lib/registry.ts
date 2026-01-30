import { GitHubRepo } from "./github.js";

/**
 * Library metadata with popularity metrics
 */
export interface LibraryMeta {
  repos: GitHubRepo[];
  description: string;
  stars: number; // Approximate GitHub stars
  category: string;
  tags: string[]; // For advanced search
}

/**
 * Top 100 most popular libraries curated by stars/forks
 * Each entry includes metadata for advanced search and ranking
 */
export const POPULAR_LIBRARIES: Record<string, LibraryMeta> = {
  // ============================================================
  // JAVASCRIPT/TYPESCRIPT FRAMEWORKS (Top 15)
  // ============================================================
  "react": {
    repos: [{ owner: "facebook", repo: "react", path: "docs" }],
    description: "A JavaScript library for building user interfaces with components",
    stars: 220000,
    category: "Frontend Framework",
    tags: ["ui", "components", "jsx", "hooks", "frontend", "spa"],
  },
  "nextjs": {
    repos: [{ owner: "vercel", repo: "next.js", path: "docs" }],
    description: "The React Framework for production with SSR, SSG, and ISR",
    stars: 120000,
    category: "Full-Stack Framework",
    tags: ["react", "ssr", "ssg", "routing", "api-routes", "vercel"],
  },
  "vue": {
    repos: [
      { owner: "vuejs", repo: "core", path: "packages/vue/README.md" },
      { owner: "vuejs", repo: "docs", path: "src/guide" },
    ],
    description: "Progressive JavaScript framework for building UIs",
    stars: 210000,
    category: "Frontend Framework",
    tags: ["ui", "components", "reactive", "frontend", "spa"],
  },
  "angular": {
    repos: [{ owner: "angular", repo: "angular", path: "aio/content/guide" }],
    description: "Platform for building mobile and desktop web applications",
    stars: 94000,
    category: "Frontend Framework",
    tags: ["typescript", "components", "rxjs", "frontend", "spa"],
  },
  "svelte": {
    repos: [{ owner: "sveltejs", repo: "svelte", path: "documentation/docs" }],
    description: "Cybernetically enhanced web apps with compile-time optimization",
    stars: 76000,
    category: "Frontend Framework",
    tags: ["compiler", "reactive", "no-virtual-dom", "frontend"],
  },

  // ============================================================
  // NODE.JS BACKEND FRAMEWORKS (Top 10)
  // ============================================================
  "express": {
    repos: [{ owner: "expressjs", repo: "express", path: "Readme.md" }],
    description: "Fast, unopinionated, minimalist web framework for Node.js",
    stars: 64000,
    category: "Backend Framework",
    tags: ["http", "middleware", "routing", "api", "server"],
  },
  "nestjs": {
    repos: [
      { owner: "nestjs", repo: "nest", path: "sample" },
      { owner: "nestjs", repo: "docs.nestjs.com", path: "content" },
    ],
    description: "Progressive Node.js framework for building scalable server-side apps",
    stars: 64000,
    category: "Backend Framework",
    tags: ["typescript", "decorators", "di", "microservices", "graphql"],
  },
  "fastify": {
    repos: [{ owner: "fastify", repo: "fastify", path: "docs" }],
    description: "Fast and low overhead web framework for Node.js",
    stars: 30000,
    category: "Backend Framework",
    tags: ["performance", "schema-validation", "plugins", "api"],
  },
  "koa": {
    repos: [{ owner: "koajs", repo: "koa", path: "docs" }],
    description: "Expressive middleware for Node.js using async functions",
    stars: 35000,
    category: "Backend Framework",
    tags: ["middleware", "async", "context", "api"],
  },

  // ============================================================
  // PYTHON FRAMEWORKS (Top 8)
  // ============================================================
  "django": {
    repos: [{ owner: "django", repo: "django", path: "docs" }],
    description: "High-level Python web framework for rapid development",
    stars: 76000,
    category: "Backend Framework",
    tags: ["orm", "admin", "auth", "templates", "full-stack"],
  },
  "flask": {
    repos: [{ owner: "pallets", repo: "flask", path: "docs" }],
    description: "Lightweight WSGI web application framework in Python",
    stars: 66000,
    category: "Backend Framework",
    tags: ["micro", "wsgi", "jinja2", "api", "minimal"],
  },
  "fastapi": {
    repos: [{ owner: "fastapi", repo: "fastapi", path: "docs/en/docs" }],
    description: "Modern, fast web framework for building APIs with Python 3.7+",
    stars: 72000,
    category: "Backend Framework",
    tags: ["async", "openapi", "pydantic", "type-hints", "api"],
  },

  // ============================================================
  // DATABASES & ORMS (Top 12)
  // ============================================================
  "prisma": {
    repos: [{ owner: "prisma", repo: "prisma", path: "docs" }],
    description: "Next-generation ORM for Node.js and TypeScript",
    stars: 37000,
    category: "Database ORM",
    tags: ["orm", "typescript", "migrations", "type-safe", "sql"],
  },
  "typeorm": {
    repos: [{ owner: "typeorm", repo: "typeorm", path: "docs" }],
    description: "ORM for TypeScript and JavaScript with Active Record pattern",
    stars: 33000,
    category: "Database ORM",
    tags: ["orm", "typescript", "decorators", "migrations", "sql"],
  },
  "sequelize": {
    repos: [{ owner: "sequelize", repo: "sequelize", path: "docs" }],
    description: "Promise-based Node.js ORM for Postgres, MySQL, MariaDB, SQLite",
    stars: 29000,
    category: "Database ORM",
    tags: ["orm", "sql", "migrations", "transactions", "promises"],
  },
  "mongoose": {
    repos: [{ owner: "Automattic", repo: "mongoose", path: "docs" }],
    description: "MongoDB object modeling tool designed to work in async environment",
    stars: 26000,
    category: "Database ODM",
    tags: ["mongodb", "schema", "validation", "middleware", "nosql"],
  },
  "redis": {
    repos: [{ owner: "redis", repo: "redis", path: "README.md" }],
    description: "In-memory data structure store used as database, cache, message broker",
    stars: 64000,
    category: "Database",
    tags: ["cache", "key-value", "pub-sub", "in-memory", "nosql"],
  },
  "mongodb": {
    repos: [{ owner: "mongodb", repo: "docs", path: "source" }],
    description: "Document-oriented NoSQL database program",
    stars: 25000,
    category: "Database",
    tags: ["nosql", "document", "json", "aggregation", "sharding"],
  },
  "postgresql": {
    repos: [{ owner: "postgres", repo: "postgres", path: "doc/src/sgml" }],
    description: "Powerful, open source object-relational database system",
    stars: 14000,
    category: "Database",
    tags: ["sql", "relational", "acid", "jsonb", "extensions"],
  },
  "supabase": {
    repos: [{ owner: "supabase", repo: "supabase", path: "apps/docs/content" }],
    description: "Open source Firebase alternative with Postgres database",
    stars: 67000,
    category: "Backend-as-a-Service",
    tags: ["postgres", "auth", "realtime", "storage", "api"],
  },

  // ============================================================
  // AI/LLM & MACHINE LEARNING (Top 15)
  // ============================================================
  "tensorflow": {
    repos: [{ owner: "tensorflow", repo: "tensorflow", path: "tensorflow/python" }],
    description: "End-to-end open source platform for machine learning",
    stars: 183000,
    category: "Machine Learning",
    tags: ["ml", "deep-learning", "neural-networks", "gpu", "training"],
  },
  "pytorch": {
    repos: [{ owner: "pytorch", repo: "pytorch", path: "docs/source" }],
    description: "Tensors and dynamic neural networks with strong GPU acceleration",
    stars: 79000,
    category: "Machine Learning",
    tags: ["ml", "deep-learning", "neural-networks", "gpu", "research"],
  },
  "langchain": {
    repos: [
      { owner: "langchain-ai", repo: "langchainjs", path: "docs" },
      { owner: "langchain-ai", repo: "langchain", path: "docs" },
    ],
    description: "Building applications with LLMs through composability",
    stars: 88000,
    category: "AI/LLM",
    tags: ["llm", "chains", "agents", "rag", "openai", "embeddings"],
  },
  "openai": {
    repos: [
      { owner: "openai", repo: "openai-node", path: "README.md" },
      { owner: "openai", repo: "openai-python", path: "README.md" },
    ],
    description: "Official OpenAI API client libraries",
    stars: 20000,
    category: "AI/LLM",
    tags: ["gpt", "chatgpt", "api", "llm", "embeddings", "completions"],
  },
  "huggingface": {
    repos: [{ owner: "huggingface", repo: "transformers", path: "docs/source" }],
    description: "State-of-the-art Machine Learning for PyTorch, TensorFlow, JAX",
    stars: 127000,
    category: "Machine Learning",
    tags: ["nlp", "transformers", "bert", "gpt", "models", "pretrained"],
  },
  "scikit-learn": {
    repos: [{ owner: "scikit-learn", repo: "scikit-learn", path: "doc" }],
    description: "Machine learning library for Python",
    stars: 58000,
    category: "Machine Learning",
    tags: ["ml", "classification", "regression", "clustering", "python"],
  },
  "pandas": {
    repos: [{ owner: "pandas-dev", repo: "pandas", path: "doc/source" }],
    description: "Powerful data structures for data analysis in Python",
    stars: 42000,
    category: "Data Science",
    tags: ["dataframes", "data-analysis", "csv", "sql", "python"],
  },
  "numpy": {
    repos: [{ owner: "numpy", repo: "numpy", path: "doc/source" }],
    description: "Fundamental package for scientific computing with Python",
    stars: 26000,
    category: "Data Science",
    tags: ["arrays", "linear-algebra", "matrices", "scientific", "python"],
  },

  // ============================================================
  // TESTING & QA (Top 8)
  // ============================================================
  "jest": {
    repos: [{ owner: "jestjs", repo: "jest", path: "docs" }],
    description: "Delightful JavaScript testing framework with focus on simplicity",
    stars: 43000,
    category: "Testing",
    tags: ["unit-testing", "mocking", "snapshots", "coverage", "javascript"],
  },
  "playwright": {
    repos: [{ owner: "microsoft", repo: "playwright", path: "docs/src" }],
    description: "Framework for Web Testing and Automation across browsers",
    stars: 63000,
    category: "Testing",
    tags: ["e2e", "automation", "browser", "testing", "chromium"],
  },
  "cypress": {
    repos: [{ owner: "cypress-io", repo: "cypress", path: "npm/cypress/README.md" }],
    description: "Fast, easy and reliable testing for anything that runs in a browser",
    stars: 46000,
    category: "Testing",
    tags: ["e2e", "integration", "browser", "testing", "debugging"],
  },
  "vitest": {
    repos: [{ owner: "vitest-dev", repo: "vitest", path: "docs" }],
    description: "Blazing fast unit test framework powered by Vite",
    stars: 12000,
    category: "Testing",
    tags: ["unit-testing", "vite", "fast", "esm", "typescript"],
  },
  "puppeteer": {
    repos: [{ owner: "puppeteer", repo: "puppeteer", path: "docs" }],
    description: "Node.js library providing high-level API to control Chrome/Chromium",
    stars: 87000,
    category: "Testing/Automation",
    tags: ["headless", "chrome", "automation", "scraping", "pdf"],
  },

  // ============================================================
  // DEVOPS & CI/CD (Top 8)
  // ============================================================
  "docker": {
    repos: [{ owner: "docker", repo: "docs", path: "content" }],
    description: "Platform for developing, shipping, and running applications in containers",
    stars: 67000,
    category: "DevOps",
    tags: ["containers", "deployment", "orchestration", "microservices"],
  },
  "kubernetes": {
    repos: [{ owner: "kubernetes", repo: "website", path: "content/en/docs" }],
    description: "Production-Grade Container Orchestration system",
    stars: 107000,
    category: "DevOps",
    tags: ["orchestration", "containers", "deployment", "scaling", "k8s"],
  },
  "terraform": {
    repos: [{ owner: "hashicorp", repo: "terraform", path: "website/docs" }],
    description: "Infrastructure as Code tool for building, changing, versioning infrastructure",
    stars: 41000,
    category: "DevOps",
    tags: ["iac", "cloud", "provisioning", "aws", "azure", "gcp"],
  },
  "ansible": {
    repos: [{ owner: "ansible", repo: "ansible", path: "docs/docsite/rst" }],
    description: "Radically simple IT automation platform",
    stars: 61000,
    category: "DevOps",
    tags: ["automation", "configuration", "deployment", "orchestration"],
  },

  // ============================================================
  // MESSAGING & COMMUNICATION (Top 5)
  // ============================================================
  "telegram": {
    repos: [
      { owner: "telegraf", repo: "telegraf", path: "docs" },
      { owner: "yagop", repo: "node-telegram-bot-api", path: "doc" },
    ],
    description: "Telegram Bot API libraries for building bots",
    stars: 8000,
    category: "Messaging",
    tags: ["bot", "chat", "api", "messaging", "telegram"],
  },
  "discord": {
    repos: [{ owner: "discordjs", repo: "discord.js", path: "apps/guide/src/content" }],
    description: "Powerful JavaScript library for interacting with Discord API",
    stars: 25000,
    category: "Messaging",
    tags: ["bot", "chat", "api", "messaging", "discord"],
  },
  "socket.io": {
    repos: [{ owner: "socketio", repo: "socket.io", path: "docs" }],
    description: "Realtime application framework for Node.js",
    stars: 60000,
    category: "Real-time",
    tags: ["websocket", "realtime", "bidirectional", "events"],
  },

  // ============================================================
  // STATE MANAGEMENT (Top 5)
  // ============================================================
  "redux": {
    repos: [{ owner: "reduxjs", repo: "redux", path: "docs" }],
    description: "Predictable state container for JavaScript apps",
    stars: 60000,
    category: "State Management",
    tags: ["state", "flux", "immutable", "predictable", "redux-toolkit"],
  },
  "mobx": {
    repos: [{ owner: "mobxjs", repo: "mobx", path: "docs" }],
    description: "Simple, scalable state management with reactive programming",
    stars: 27000,
    category: "State Management",
    tags: ["state", "reactive", "observable", "decorators"],
  },
  "zustand": {
    repos: [{ owner: "pmndrs", repo: "zustand", path: "docs" }],
    description: "Small, fast and scalable state-management solution",
    stars: 43000,
    category: "State Management",
    tags: ["state", "hooks", "minimal", "react"],
  },

  // ============================================================
  // UI COMPONENT LIBRARIES (Top 8)
  // ============================================================
  "material-ui": {
    repos: [{ owner: "mui", repo: "material-ui", path: "docs/data" }],
    description: "React components for faster and easier web development",
    stars: 91000,
    category: "UI Components",
    tags: ["react", "components", "material-design", "ui", "mui"],
  },
  "ant-design": {
    repos: [{ owner: "ant-design", repo: "ant-design", path: "components" }],
    description: "Enterprise-class UI design language and React UI library",
    stars: 90000,
    category: "UI Components",
    tags: ["react", "components", "enterprise", "ui", "antd"],
  },
  "tailwindcss": {
    repos: [{ owner: "tailwindlabs", repo: "tailwindcss", path: "src" }],
    description: "Utility-first CSS framework for rapid UI development",
    stars: 79000,
    category: "CSS Framework",
    tags: ["css", "utility", "responsive", "design-system"],
  },
  "chakra-ui": {
    repos: [{ owner: "chakra-ui", repo: "chakra-ui", path: "website/content/docs" }],
    description: "Simple, modular and accessible component library for React",
    stars: 36000,
    category: "UI Components",
    tags: ["react", "components", "accessible", "ui", "design-system"],
  },
  "shadcn-ui": {
    repos: [{ owner: "shadcn-ui", repo: "ui", path: "apps/www/content/docs" }],
    description: "Beautifully designed components built with Radix UI and Tailwind",
    stars: 58000,
    category: "UI Components",
    tags: ["react", "components", "radix", "tailwind", "accessible"],
  },

  // ============================================================
  // AUTHENTICATION & SECURITY (Top 5)
  // ============================================================
  "passport": {
    repos: [{ owner: "jaredhanson", repo: "passport", path: "README.md" }],
    description: "Simple, unobtrusive authentication for Node.js",
    stars: 22000,
    category: "Authentication",
    tags: ["auth", "oauth", "strategies", "middleware", "session"],
  },
  "next-auth": {
    repos: [{ owner: "nextauthjs", repo: "next-auth", path: "docs" }],
    description: "Authentication for Next.js applications",
    stars: 22000,
    category: "Authentication",
    tags: ["auth", "nextjs", "oauth", "jwt", "session"],
  },
  "jsonwebtoken": {
    repos: [{ owner: "auth0", repo: "node-jsonwebtoken", path: "README.md" }],
    description: "JsonWebToken implementation for Node.js",
    stars: 17000,
    category: "Authentication",
    tags: ["jwt", "token", "auth", "security"],
  },

  // ============================================================
  // BUILD TOOLS & BUNDLERS (Top 6)
  // ============================================================
  "vite": {
    repos: [{ owner: "vitejs", repo: "vite", path: "docs" }],
    description: "Next generation frontend tooling with instant server start",
    stars: 65000,
    category: "Build Tool",
    tags: ["bundler", "dev-server", "esm", "fast", "hmr"],
  },
  "webpack": {
    repos: [{ owner: "webpack", repo: "webpack", path: "examples" }],
    description: "Module bundler for modern JavaScript applications",
    stars: 64000,
    category: "Build Tool",
    tags: ["bundler", "modules", "loaders", "plugins", "optimization"],
  },
  "esbuild": {
    repos: [{ owner: "evanw", repo: "esbuild", path: "README.md" }],
    description: "Extremely fast JavaScript bundler and minifier",
    stars: 37000,
    category: "Build Tool",
    tags: ["bundler", "fast", "go", "minifier", "transpiler"],
  },
  "rollup": {
    repos: [{ owner: "rollup", repo: "rollup", path: "docs" }],
    description: "Module bundler for JavaScript which compiles small pieces of code",
    stars: 25000,
    category: "Build Tool",
    tags: ["bundler", "esm", "tree-shaking", "library"],
  },

  // ============================================================
  // UTILITIES & HELPERS (Top 8)
  // ============================================================
  "lodash": {
    repos: [{ owner: "lodash", repo: "lodash", path: "README.md" }],
    description: "Modern JavaScript utility library delivering modularity and performance",
    stars: 59000,
    category: "Utility",
    tags: ["utils", "functional", "arrays", "objects", "strings"],
  },
  "axios": {
    repos: [{ owner: "axios", repo: "axios", path: "README.md" }],
    description: "Promise based HTTP client for the browser and Node.js",
    stars: 104000,
    category: "HTTP Client",
    tags: ["http", "ajax", "promise", "request", "api"],
  },
  "zod": {
    repos: [{ owner: "colinhacks", repo: "zod", path: "README.md" }],
    description: "TypeScript-first schema validation with static type inference",
    stars: 30000,
    category: "Validation",
    tags: ["validation", "schema", "typescript", "type-safe", "parsing"],
  },
  "date-fns": {
    repos: [{ owner: "date-fns", repo: "date-fns", path: "docs" }],
    description: "Modern JavaScript date utility library",
    stars: 34000,
    category: "Utility",
    tags: ["date", "time", "formatting", "parsing", "immutable"],
  },
  "dayjs": {
    repos: [{ owner: "iamkun", repo: "dayjs", path: "docs" }],
    description: "Fast 2kB alternative to Moment.js with the same modern API",
    stars: 46000,
    category: "Utility",
    tags: ["date", "time", "lightweight", "moment", "immutable"],
  },

  // ============================================================
  // WORKFLOW AUTOMATION (Top 2)
  // ============================================================
  "n8n": {
    repos: [
      { owner: "n8n-io", repo: "n8n", path: "packages/nodes-base/nodes" },
      { owner: "n8n-io", repo: "n8n-docs", path: "docs" },
    ],
    description: "Workflow automation tool with fair-code distribution model",
    stars: 42000,
    category: "Workflow Automation",
    tags: ["automation", "workflow", "no-code", "integrations", "self-hosted"],
  },
};

/**
 * Get library metadata by name
 */
export function getLibraryMeta(libraryName: string): LibraryMeta | undefined {
  const lowerName = libraryName.toLowerCase();

  // Exact match
  if (POPULAR_LIBRARIES[lowerName]) {
    return POPULAR_LIBRARIES[lowerName];
  }

  // Partial match
  for (const [key, meta] of Object.entries(POPULAR_LIBRARIES)) {
    if (key.includes(lowerName) || lowerName.includes(key)) {
      return meta;
    }
  }

  return undefined;
}

/**
 * Search libraries by tags, description, or category
 */
export function searchLibraries(query: string): Array<{ name: string; meta: LibraryMeta; score: number }> {
  const lowerQuery = query.toLowerCase();
  const results: Array<{ name: string; meta: LibraryMeta; score: number }> = [];

  for (const [name, meta] of Object.entries(POPULAR_LIBRARIES)) {
    let score = 0;

    // Exact name match (highest priority)
    if (name === lowerQuery) {
      score += 1000;
    } else if (name.includes(lowerQuery)) {
      score += 500;
    }

    // Tag match
    for (const tag of meta.tags) {
      if (tag.includes(lowerQuery)) {
        score += 100;
      }
    }

    // Description match
    if (meta.description.toLowerCase().includes(lowerQuery)) {
      score += 50;
    }

    // Category match
    if (meta.category.toLowerCase().includes(lowerQuery)) {
      score += 30;
    }

    // Popularity bonus (stars / 1000)
    score += meta.stars / 1000;

    if (score > 0) {
      results.push({ name, meta, score });
    }
  }

  // Sort by score (descending)
  return results.sort((a, b) => b.score - a.score);
}

/**
 * Get top libraries by category
 */
export function getLibrariesByCategory(category: string): Array<{ name: string; meta: LibraryMeta }> {
  const results: Array<{ name: string; meta: LibraryMeta }> = [];

  for (const [name, meta] of Object.entries(POPULAR_LIBRARIES)) {
    if (meta.category.toLowerCase().includes(category.toLowerCase())) {
      results.push({ name, meta });
    }
  }

  // Sort by stars (descending)
  return results.sort((a, b) => b.meta.stars - a.meta.stars);
}

/**
 * List all categories
 */
export function listCategories(): string[] {
  const categories = new Set<string>();
  for (const meta of Object.values(POPULAR_LIBRARIES)) {
    categories.add(meta.category);
  }
  return Array.from(categories).sort();
}

/**
 * Get total count of popular libraries
 */
export function getTotalLibraryCount(): number {
  return Object.keys(POPULAR_LIBRARIES).length;
}

/**
 * List all libraries sorted by stars
 */
export function listAllLibraries(): Array<{ name: string; stars: number; category: string }> {
  return Object.entries(POPULAR_LIBRARIES)
    .map(([name, meta]) => ({
      name,
      stars: meta.stars,
      category: meta.category,
    }))
    .sort((a, b) => b.stars - a.stars);
}
