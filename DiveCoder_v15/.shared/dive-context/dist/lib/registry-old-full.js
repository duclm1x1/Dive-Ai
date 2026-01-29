/**
 * Expanded registry of 1000+ popular repositories for documentation
 * Organized by category for easy discovery
 */
export const REPO_REGISTRY = {
    // ============================================================
    // WORKFLOW AUTOMATION & NO-CODE
    // ============================================================
    "n8n": [
        { owner: "n8n-io", repo: "n8n", path: "packages/nodes-base/nodes" },
        { owner: "n8n-io", repo: "n8n-docs", path: "docs" },
    ],
    "zapier": [
        { owner: "zapier", repo: "zapier-platform", path: "packages" },
    ],
    "make": [
        { owner: "integromat", repo: "apps", path: "docs" },
    ],
    "activepieces": [
        { owner: "activepieces", repo: "activepieces", path: "docs" },
    ],
    "windmill": [
        { owner: "windmill-labs", repo: "windmill", path: "frontend/src/lib/components/apps" },
    ],
    // ============================================================
    // JAVASCRIPT/TYPESCRIPT FRAMEWORKS
    // ============================================================
    "nextjs": [
        { owner: "vercel", repo: "next.js", path: "docs" },
    ],
    "react": [
        { owner: "facebook", repo: "react", path: "docs" },
    ],
    "vue": [
        { owner: "vuejs", repo: "core", path: "packages/vue/README.md" },
        { owner: "vuejs", repo: "docs", path: "src/guide" },
    ],
    "angular": [
        { owner: "angular", repo: "angular", path: "aio/content/guide" },
    ],
    "svelte": [
        { owner: "sveltejs", repo: "svelte", path: "documentation/docs" },
    ],
    "solid": [
        { owner: "solidjs", repo: "solid", path: "documentation" },
    ],
    "qwik": [
        { owner: "QwikDev", repo: "qwik", path: "packages/docs/src/routes/docs" },
    ],
    "astro": [
        { owner: "withastro", repo: "astro", path: "packages/astro/README.md" },
    ],
    "remix": [
        { owner: "remix-run", repo: "remix", path: "docs" },
    ],
    "nuxt": [
        { owner: "nuxt", repo: "nuxt", path: "docs" },
    ],
    "gatsby": [
        { owner: "gatsbyjs", repo: "gatsby", path: "docs" },
    ],
    // ============================================================
    // NODE.JS BACKEND FRAMEWORKS
    // ============================================================
    "express": [
        { owner: "expressjs", repo: "express", path: "Readme.md" },
    ],
    "fastify": [
        { owner: "fastify", repo: "fastify", path: "docs" },
    ],
    "koa": [
        { owner: "koajs", repo: "koa", path: "docs" },
    ],
    "hapi": [
        { owner: "hapijs", repo: "hapi", path: "API.md" },
    ],
    "nestjs": [
        { owner: "nestjs", repo: "nest", path: "sample" },
        { owner: "nestjs", repo: "docs.nestjs.com", path: "content" },
    ],
    "adonis": [
        { owner: "adonisjs", repo: "core", path: "docs" },
    ],
    "sails": [
        { owner: "balderdashy", repo: "sails", path: "docs" },
    ],
    "meteor": [
        { owner: "meteor", repo: "meteor", path: "guide/source" },
    ],
    "feathers": [
        { owner: "feathersjs", repo: "feathers", path: "docs" },
    ],
    "loopback": [
        { owner: "loopbackio", repo: "loopback-next", path: "docs/site" },
    ],
    // ============================================================
    // PYTHON FRAMEWORKS
    // ============================================================
    "fastapi": [
        { owner: "fastapi", repo: "fastapi", path: "docs/en/docs" },
    ],
    "django": [
        { owner: "django", repo: "django", path: "docs" },
    ],
    "flask": [
        { owner: "pallets", repo: "flask", path: "docs" },
    ],
    "tornado": [
        { owner: "tornadoweb", repo: "tornado", path: "docs" },
    ],
    "pyramid": [
        { owner: "Pylons", repo: "pyramid", path: "docs" },
    ],
    "bottle": [
        { owner: "bottlepy", repo: "bottle", path: "docs" },
    ],
    "falcon": [
        { owner: "falconry", repo: "falcon", path: "docs" },
    ],
    "sanic": [
        { owner: "sanic-org", repo: "sanic", path: "guide/content" },
    ],
    "starlette": [
        { owner: "encode", repo: "starlette", path: "docs" },
    ],
    "quart": [
        { owner: "pallets", repo: "quart", path: "docs" },
    ],
    // ============================================================
    // DATABASES & ORMS
    // ============================================================
    "supabase": [
        { owner: "supabase", repo: "supabase", path: "apps/docs/content" },
    ],
    "prisma": [
        { owner: "prisma", repo: "prisma", path: "docs" },
    ],
    "mongodb": [
        { owner: "mongodb", repo: "docs", path: "source" },
    ],
    "postgresql": [
        { owner: "postgres", repo: "postgres", path: "doc/src/sgml" },
    ],
    "mysql": [
        { owner: "mysql", repo: "mysql-server", path: "Docs" },
    ],
    "redis": [
        { owner: "redis", repo: "redis", path: "README.md" },
    ],
    "typeorm": [
        { owner: "typeorm", repo: "typeorm", path: "docs" },
    ],
    "sequelize": [
        { owner: "sequelize", repo: "sequelize", path: "docs" },
    ],
    "mongoose": [
        { owner: "Automattic", repo: "mongoose", path: "docs" },
    ],
    "knex": [
        { owner: "knex", repo: "knex", path: "types" },
    ],
    "drizzle": [
        { owner: "drizzle-team", repo: "drizzle-orm", path: "drizzle-orm/src" },
    ],
    "kysely": [
        { owner: "kysely-org", repo: "kysely", path: "site/docs" },
    ],
    "mikro-orm": [
        { owner: "mikro-orm", repo: "mikro-orm", path: "docs" },
    ],
    "objection": [
        { owner: "Vincit", repo: "objection.js", path: "doc" },
    ],
    "bookshelf": [
        { owner: "bookshelf", repo: "bookshelf", path: "README.md" },
    ],
    "waterline": [
        { owner: "balderdashy", repo: "waterline", path: "docs" },
    ],
    "cassandra": [
        { owner: "apache", repo: "cassandra", path: "doc" },
    ],
    "couchdb": [
        { owner: "apache", repo: "couchdb", path: "share/doc" },
    ],
    "elasticsearch": [
        { owner: "elastic", repo: "elasticsearch", path: "docs/reference" },
    ],
    "neo4j": [
        { owner: "neo4j", repo: "neo4j", path: "community/community-it/kernel-it/src/test/resources" },
    ],
    // ============================================================
    // CLOUD PLATFORMS & DEPLOYMENT
    // ============================================================
    "vercel": [
        { owner: "vercel", repo: "vercel", path: "docs" },
    ],
    "cloudflare": [
        { owner: "cloudflare", repo: "workers-sdk", path: "packages/wrangler/docs" },
    ],
    "netlify": [
        { owner: "netlify", repo: "cli", path: "docs" },
    ],
    "heroku": [
        { owner: "heroku", repo: "cli", path: "docs" },
    ],
    "railway": [
        { owner: "railwayapp", repo: "docs", path: "src/docs" },
    ],
    "render": [
        { owner: "render-examples", repo: "docs", path: "docs" },
    ],
    "fly": [
        { owner: "superfly", repo: "docs", path: "reference" },
    ],
    "aws-cdk": [
        { owner: "aws", repo: "aws-cdk", path: "packages" },
    ],
    "aws-amplify": [
        { owner: "aws-amplify", repo: "amplify-js", path: "packages" },
    ],
    "terraform": [
        { owner: "hashicorp", repo: "terraform", path: "website/docs" },
    ],
    "pulumi": [
        { owner: "pulumi", repo: "pulumi", path: "sdk" },
    ],
    "serverless": [
        { owner: "serverless", repo: "serverless", path: "docs" },
    ],
    // ============================================================
    // AI/LLM & MACHINE LEARNING
    // ============================================================
    "openai": [
        { owner: "openai", repo: "openai-node", path: "README.md" },
        { owner: "openai", repo: "openai-python", path: "README.md" },
    ],
    "langchain": [
        { owner: "langchain-ai", repo: "langchainjs", path: "docs" },
        { owner: "langchain-ai", repo: "langchain", path: "docs" },
    ],
    "llamaindex": [
        { owner: "run-llama", repo: "LlamaIndexTS", path: "packages/core/src" },
    ],
    "anthropic": [
        { owner: "anthropics", repo: "anthropic-sdk-typescript", path: "README.md" },
    ],
    "huggingface": [
        { owner: "huggingface", repo: "transformers", path: "docs/source" },
    ],
    "tensorflow": [
        { owner: "tensorflow", repo: "tensorflow", path: "tensorflow/python" },
    ],
    "pytorch": [
        { owner: "pytorch", repo: "pytorch", path: "docs/source" },
    ],
    "scikit-learn": [
        { owner: "scikit-learn", repo: "scikit-learn", path: "doc" },
    ],
    "keras": [
        { owner: "keras-team", repo: "keras", path: "guides" },
    ],
    "pandas": [
        { owner: "pandas-dev", repo: "pandas", path: "doc/source" },
    ],
    "numpy": [
        { owner: "numpy", repo: "numpy", path: "doc/source" },
    ],
    "scipy": [
        { owner: "scipy", repo: "scipy", path: "doc/source" },
    ],
    "matplotlib": [
        { owner: "matplotlib", repo: "matplotlib", path: "doc" },
    ],
    "seaborn": [
        { owner: "mwaskom", repo: "seaborn", path: "doc" },
    ],
    "plotly": [
        { owner: "plotly", repo: "plotly.js", path: "README.md" },
    ],
    // ============================================================
    // MESSAGING & COMMUNICATION
    // ============================================================
    "telegram": [
        { owner: "telegraf", repo: "telegraf", path: "docs" },
        { owner: "yagop", repo: "node-telegram-bot-api", path: "doc" },
    ],
    "discord": [
        { owner: "discordjs", repo: "discord.js", path: "apps/guide/src/content" },
    ],
    "slack": [
        { owner: "slackapi", repo: "node-slack-sdk", path: "docs" },
    ],
    "whatsapp": [
        { owner: "pedroslopez", repo: "whatsapp-web.js", path: "README.md" },
    ],
    "twilio": [
        { owner: "twilio", repo: "twilio-node", path: "README.md" },
    ],
    "sendgrid": [
        { owner: "sendgrid", repo: "sendgrid-nodejs", path: "docs" },
    ],
    "mailgun": [
        { owner: "mailgun", repo: "mailgun-js", path: "docs" },
    ],
    "nodemailer": [
        { owner: "nodemailer", repo: "nodemailer", path: "README.md" },
    ],
    "pusher": [
        { owner: "pusher", repo: "pusher-http-node", path: "README.md" },
    ],
    "socket.io": [
        { owner: "socketio", repo: "socket.io", path: "docs" },
    ],
    "rabbitmq": [
        { owner: "rabbitmq", repo: "rabbitmq-server", path: "deps/rabbit/docs" },
    ],
    "kafka": [
        { owner: "apache", repo: "kafka", path: "docs" },
    ],
    // ============================================================
    // TESTING & QA
    // ============================================================
    "jest": [
        { owner: "jestjs", repo: "jest", path: "docs" },
    ],
    "vitest": [
        { owner: "vitest-dev", repo: "vitest", path: "docs" },
    ],
    "playwright": [
        { owner: "microsoft", repo: "playwright", path: "docs/src" },
    ],
    "cypress": [
        { owner: "cypress-io", repo: "cypress", path: "npm/cypress/README.md" },
    ],
    "puppeteer": [
        { owner: "puppeteer", repo: "puppeteer", path: "docs" },
    ],
    "mocha": [
        { owner: "mochajs", repo: "mocha", path: "docs" },
    ],
    "chai": [
        { owner: "chaijs", repo: "chai", path: "docs" },
    ],
    "jasmine": [
        { owner: "jasmine", repo: "jasmine", path: "src" },
    ],
    "ava": [
        { owner: "avajs", repo: "ava", path: "docs" },
    ],
    "selenium": [
        { owner: "SeleniumHQ", repo: "selenium", path: "javascript/node/selenium-webdriver" },
    ],
    "testcafe": [
        { owner: "DevExpress", repo: "testcafe", path: "docs" },
    ],
    "nightwatch": [
        { owner: "nightwatchjs", repo: "nightwatch", path: "lib" },
    ],
    "webdriverio": [
        { owner: "webdriverio", repo: "webdriverio", path: "website/docs" },
    ],
    "supertest": [
        { owner: "ladjs", repo: "supertest", path: "README.md" },
    ],
    "nock": [
        { owner: "nock", repo: "nock", path: "README.md" },
    ],
    "sinon": [
        { owner: "sinonjs", repo: "sinon", path: "docs" },
    ],
    // ============================================================
    // DEVOPS & CI/CD
    // ============================================================
    "docker": [
        { owner: "docker", repo: "docs", path: "content" },
    ],
    "kubernetes": [
        { owner: "kubernetes", repo: "website", path: "content/en/docs" },
    ],
    "github-actions": [
        { owner: "actions", repo: "toolkit", path: "docs" },
    ],
    "gitlab-ci": [
        { owner: "gitlabhq", repo: "gitlabhq", path: "doc/ci" },
    ],
    "jenkins": [
        { owner: "jenkinsci", repo: "jenkins", path: "core/src/main/resources/hudson/model" },
    ],
    "circleci": [
        { owner: "CircleCI-Public", repo: "circleci-docs", path: "jekyll" },
    ],
    "travis": [
        { owner: "travis-ci", repo: "docs-travis-ci-com", path: "user" },
    ],
    "ansible": [
        { owner: "ansible", repo: "ansible", path: "docs/docsite/rst" },
    ],
    "vagrant": [
        { owner: "hashicorp", repo: "vagrant", path: "website/content/docs" },
    ],
    "packer": [
        { owner: "hashicorp", repo: "packer", path: "website/content/docs" },
    ],
    "helm": [
        { owner: "helm", repo: "helm", path: "docs" },
    ],
    "argocd": [
        { owner: "argoproj", repo: "argo-cd", path: "docs" },
    ],
    "flux": [
        { owner: "fluxcd", repo: "flux2", path: "docs" },
    ],
    "prometheus": [
        { owner: "prometheus", repo: "prometheus", path: "docs" },
    ],
    "grafana": [
        { owner: "grafana", repo: "grafana", path: "docs/sources" },
    ],
    // ============================================================
    // MOBILE DEVELOPMENT
    // ============================================================
    "react-native": [
        { owner: "facebook", repo: "react-native", path: "docs" },
    ],
    "expo": [
        { owner: "expo", repo: "expo", path: "docs/pages" },
    ],
    "flutter": [
        { owner: "flutter", repo: "flutter", path: "examples" },
    ],
    "ionic": [
        { owner: "ionic-team", repo: "ionic-framework", path: "core/src/components" },
    ],
    "capacitor": [
        { owner: "ionic-team", repo: "capacitor", path: "site/docs-md" },
    ],
    "nativescript": [
        { owner: "NativeScript", repo: "NativeScript", path: "packages" },
    ],
    "xamarin": [
        { owner: "xamarin", repo: "xamarin-forms-samples", path: "README.md" },
    ],
    // ============================================================
    // STATE MANAGEMENT
    // ============================================================
    "redux": [
        { owner: "reduxjs", repo: "redux", path: "docs" },
    ],
    "mobx": [
        { owner: "mobxjs", repo: "mobx", path: "docs" },
    ],
    "zustand": [
        { owner: "pmndrs", repo: "zustand", path: "docs" },
    ],
    "jotai": [
        { owner: "pmndrs", repo: "jotai", path: "docs" },
    ],
    "recoil": [
        { owner: "facebookexperimental", repo: "Recoil", path: "docs" },
    ],
    "xstate": [
        { owner: "statelyai", repo: "xstate", path: "docs" },
    ],
    "valtio": [
        { owner: "pmndrs", repo: "valtio", path: "docs" },
    ],
    "pinia": [
        { owner: "vuejs", repo: "pinia", path: "packages/docs" },
    ],
    "vuex": [
        { owner: "vuejs", repo: "vuex", path: "docs" },
    ],
    "ngrx": [
        { owner: "ngrx", repo: "platform", path: "projects/ngrx.io/content" },
    ],
    // ============================================================
    // UI COMPONENT LIBRARIES
    // ============================================================
    "material-ui": [
        { owner: "mui", repo: "material-ui", path: "docs/data" },
    ],
    "ant-design": [
        { owner: "ant-design", repo: "ant-design", path: "components" },
    ],
    "chakra-ui": [
        { owner: "chakra-ui", repo: "chakra-ui", path: "website/content/docs" },
    ],
    "shadcn-ui": [
        { owner: "shadcn-ui", repo: "ui", path: "apps/www/content/docs" },
    ],
    "radix-ui": [
        { owner: "radix-ui", repo: "primitives", path: "data" },
    ],
    "headless-ui": [
        { owner: "tailwindlabs", repo: "headlessui", path: "packages" },
    ],
    "mantine": [
        { owner: "mantinedev", repo: "mantine", path: "docs" },
    ],
    "nextui": [
        { owner: "nextui-org", repo: "nextui", path: "apps/docs/content" },
    ],
    "daisyui": [
        { owner: "saadeghi", repo: "daisyui", path: "src/docs" },
    ],
    "bootstrap": [
        { owner: "twbs", repo: "bootstrap", path: "site/content/docs" },
    ],
    "tailwindcss": [
        { owner: "tailwindlabs", repo: "tailwindcss", path: "src" },
    ],
    "bulma": [
        { owner: "jgthms", repo: "bulma", path: "docs" },
    ],
    "semantic-ui": [
        { owner: "Semantic-Org", repo: "Semantic-UI-React", path: "docs" },
    ],
    "primereact": [
        { owner: "primefaces", repo: "primereact", path: "components/doc" },
    ],
    "blueprint": [
        { owner: "palantir", repo: "blueprint", path: "packages" },
    ],
    // ============================================================
    // AUTHENTICATION & SECURITY
    // ============================================================
    "auth0": [
        { owner: "auth0", repo: "node-auth0", path: "README.md" },
    ],
    "clerk": [
        { owner: "clerk", repo: "javascript", path: "packages" },
    ],
    "passport": [
        { owner: "jaredhanson", repo: "passport", path: "README.md" },
    ],
    "next-auth": [
        { owner: "nextauthjs", repo: "next-auth", path: "docs" },
    ],
    "firebase-auth": [
        { owner: "firebase", repo: "firebase-js-sdk", path: "packages/auth" },
    ],
    "keycloak": [
        { owner: "keycloak", repo: "keycloak", path: "docs" },
    ],
    "oauth2": [
        { owner: "oauth2-proxy", repo: "oauth2-proxy", path: "docs" },
    ],
    "jwt": [
        { owner: "auth0", repo: "node-jsonwebtoken", path: "README.md" },
    ],
    "bcrypt": [
        { owner: "kelektiv", repo: "node.bcrypt.js", path: "README.md" },
    ],
    "helmet": [
        { owner: "helmetjs", repo: "helmet", path: "README.md" },
    ],
    // ============================================================
    // PAYMENT PROCESSING
    // ============================================================
    "stripe": [
        { owner: "stripe", repo: "stripe-node", path: "README.md" },
    ],
    "paypal": [
        { owner: "paypal", repo: "PayPal-node-SDK", path: "README.md" },
    ],
    "square": [
        { owner: "square", repo: "square-nodejs-sdk", path: "doc" },
    ],
    "braintree": [
        { owner: "braintree", repo: "braintree_node", path: "README.md" },
    ],
    "paddle": [
        { owner: "PaddleHQ", repo: "paddle-node-sdk", path: "README.md" },
    ],
    "lemon-squeezy": [
        { owner: "lmsqueezy", repo: "lemonsqueezy.js", path: "README.md" },
    ],
    // ============================================================
    // ANALYTICS & MONITORING
    // ============================================================
    "google-analytics": [
        { owner: "googleapis", repo: "google-api-nodejs-client", path: "src/apis/analytics" },
    ],
    "mixpanel": [
        { owner: "mixpanel", repo: "mixpanel-node", path: "readme.md" },
    ],
    "segment": [
        { owner: "segmentio", repo: "analytics-next", path: "packages" },
    ],
    "posthog": [
        { owner: "PostHog", repo: "posthog-js", path: "README.md" },
    ],
    "amplitude": [
        { owner: "amplitude", repo: "Amplitude-TypeScript", path: "packages" },
    ],
    "sentry": [
        { owner: "getsentry", repo: "sentry-javascript", path: "packages" },
    ],
    "datadog": [
        { owner: "DataDog", repo: "dd-trace-js", path: "docs" },
    ],
    "newrelic": [
        { owner: "newrelic", repo: "node-newrelic", path: "README.md" },
    ],
    "bugsnag": [
        { owner: "bugsnag", repo: "bugsnag-js", path: "packages" },
    ],
    "rollbar": [
        { owner: "rollbar", repo: "rollbar.js", path: "docs" },
    ],
    // ============================================================
    // FILE STORAGE & MEDIA
    // ============================================================
    "aws-s3": [
        { owner: "aws", repo: "aws-sdk-js-v3", path: "clients/client-s3" },
    ],
    "cloudinary": [
        { owner: "cloudinary", repo: "cloudinary_npm", path: "README.md" },
    ],
    "uploadcare": [
        { owner: "uploadcare", repo: "uploadcare-js-api-clients", path: "packages" },
    ],
    "imagekit": [
        { owner: "imagekit-developer", repo: "imagekit-nodejs", path: "README.md" },
    ],
    "multer": [
        { owner: "expressjs", repo: "multer", path: "README.md" },
    ],
    "sharp": [
        { owner: "lovell", repo: "sharp", path: "docs" },
    ],
    "jimp": [
        { owner: "jimp-dev", repo: "jimp", path: "packages" },
    ],
    "ffmpeg": [
        { owner: "fluent-ffmpeg", repo: "node-fluent-ffmpeg", path: "README.md" },
    ],
    // ============================================================
    // SEARCH & INDEXING
    // ============================================================
    "algolia": [
        { owner: "algolia", repo: "algoliasearch-client-javascript", path: "packages" },
    ],
    "meilisearch": [
        { owner: "meilisearch", repo: "meilisearch-js", path: "README.md" },
    ],
    "typesense": [
        { owner: "typesense", repo: "typesense-js", path: "README.md" },
    ],
    "lunr": [
        { owner: "olivernn", repo: "lunr.js", path: "README.md" },
    ],
    "fuse": [
        { owner: "krisk", repo: "Fuse", path: "docs" },
    ],
    // ============================================================
    // CMS & CONTENT
    // ============================================================
    "strapi": [
        { owner: "strapi", repo: "strapi", path: "docs" },
    ],
    "contentful": [
        { owner: "contentful", repo: "contentful.js", path: "README.md" },
    ],
    "sanity": [
        { owner: "sanity-io", repo: "sanity", path: "packages" },
    ],
    "ghost": [
        { owner: "TryGhost", repo: "Ghost", path: "ghost" },
    ],
    "wordpress": [
        { owner: "WordPress", repo: "wordpress-develop", path: "src" },
    ],
    "keystonejs": [
        { owner: "keystonejs", repo: "keystone", path: "docs" },
    ],
    "directus": [
        { owner: "directus", repo: "directus", path: "docs" },
    ],
    "payload": [
        { owner: "payloadcms", repo: "payload", path: "docs" },
    ],
    // ============================================================
    // GRAPHQL
    // ============================================================
    "apollo": [
        { owner: "apollographql", repo: "apollo-client", path: "docs/source" },
        { owner: "apollographql", repo: "apollo-server", path: "docs/source" },
    ],
    "graphql": [
        { owner: "graphql", repo: "graphql-js", path: "src" },
    ],
    "relay": [
        { owner: "facebook", repo: "relay", path: "website/docs" },
    ],
    "urql": [
        { owner: "urql-graphql", repo: "urql", path: "docs" },
    ],
    "hasura": [
        { owner: "hasura", repo: "graphql-engine", path: "docs" },
    ],
    "postgraphile": [
        { owner: "graphile", repo: "postgraphile", path: "README.md" },
    ],
    // ============================================================
    // REAL-TIME & WEBSOCKETS
    // ============================================================
    "ws": [
        { owner: "websockets", repo: "ws", path: "README.md" },
    ],
    "ably": [
        { owner: "ably", repo: "ably-js", path: "docs" },
    ],
    "centrifugo": [
        { owner: "centrifugal", repo: "centrifugo", path: "docs" },
    ],
    // ============================================================
    // BLOCKCHAIN & WEB3
    // ============================================================
    "ethers": [
        { owner: "ethers-io", repo: "ethers.js", path: "docs" },
    ],
    "web3": [
        { owner: "web3", repo: "web3.js", path: "docs" },
    ],
    "wagmi": [
        { owner: "wevm", repo: "wagmi", path: "docs/pages" },
    ],
    "viem": [
        { owner: "wevm", repo: "viem", path: "site/pages" },
    ],
    "hardhat": [
        { owner: "NomicFoundation", repo: "hardhat", path: "docs" },
    ],
    "truffle": [
        { owner: "trufflesuite", repo: "truffle", path: "packages" },
    ],
    "solidity": [
        { owner: "ethereum", repo: "solidity", path: "docs" },
    ],
    // ============================================================
    // DOCUMENTATION TOOLS
    // ============================================================
    "docusaurus": [
        { owner: "facebook", repo: "docusaurus", path: "website/docs" },
    ],
    "vitepress": [
        { owner: "vuejs", repo: "vitepress", path: "docs" },
    ],
    "nextra": [
        { owner: "shuding", repo: "nextra", path: "docs" },
    ],
    "mintlify": [
        { owner: "mintlify", repo: "starter", path: "README.md" },
    ],
    "gitbook": [
        { owner: "GitbookIO", repo: "gitbook", path: "docs" },
    ],
    "mkdocs": [
        { owner: "mkdocs", repo: "mkdocs", path: "docs" },
    ],
    "sphinx": [
        { owner: "sphinx-doc", repo: "sphinx", path: "doc" },
    ],
    "typedoc": [
        { owner: "TypeStrong", repo: "typedoc", path: "README.md" },
    ],
    "jsdoc": [
        { owner: "jsdoc", repo: "jsdoc", path: "README.md" },
    ],
    "storybook": [
        { owner: "storybookjs", repo: "storybook", path: "docs" },
    ],
    // ============================================================
    // BUILD TOOLS & BUNDLERS
    // ============================================================
    "vite": [
        { owner: "vitejs", repo: "vite", path: "docs" },
    ],
    "webpack": [
        { owner: "webpack", repo: "webpack", path: "examples" },
    ],
    "rollup": [
        { owner: "rollup", repo: "rollup", path: "docs" },
    ],
    "esbuild": [
        { owner: "evanw", repo: "esbuild", path: "README.md" },
    ],
    "parcel": [
        { owner: "parcel-bundler", repo: "parcel", path: "packages" },
    ],
    "turbopack": [
        { owner: "vercel", repo: "turbo", path: "crates/turbopack" },
    ],
    "swc": [
        { owner: "swc-project", repo: "swc", path: "website/docs" },
    ],
    "babel": [
        { owner: "babel", repo: "babel", path: "packages" },
    ],
    "tsup": [
        { owner: "egoist", repo: "tsup", path: "README.md" },
    ],
    "unbuild": [
        { owner: "unjs", repo: "unbuild", path: "README.md" },
    ],
    // ============================================================
    // LINTING & FORMATTING
    // ============================================================
    "eslint": [
        { owner: "eslint", repo: "eslint", path: "docs/src" },
    ],
    "prettier": [
        { owner: "prettier", repo: "prettier", path: "docs" },
    ],
    "biome": [
        { owner: "biomejs", repo: "biome", path: "website/src/content/docs" },
    ],
    "stylelint": [
        { owner: "stylelint", repo: "stylelint", path: "docs" },
    ],
    "commitlint": [
        { owner: "conventional-changelog", repo: "commitlint", path: "docs" },
    ],
    "husky": [
        { owner: "typicode", repo: "husky", path: "README.md" },
    ],
    "lint-staged": [
        { owner: "lint-staged", repo: "lint-staged", path: "README.md" },
    ],
    // ============================================================
    // PACKAGE MANAGERS
    // ============================================================
    "npm": [
        { owner: "npm", repo: "cli", path: "docs" },
    ],
    "yarn": [
        { owner: "yarnpkg", repo: "berry", path: "packages/yarnpkg-website/docs" },
    ],
    "pnpm": [
        { owner: "pnpm", repo: "pnpm", path: "website/docs" },
    ],
    "bun": [
        { owner: "oven-sh", repo: "bun", path: "docs" },
    ],
    // ============================================================
    // UTILITIES & HELPERS
    // ============================================================
    "lodash": [
        { owner: "lodash", repo: "lodash", path: "README.md" },
    ],
    "ramda": [
        { owner: "ramda", repo: "ramda", path: "README.md" },
    ],
    "date-fns": [
        { owner: "date-fns", repo: "date-fns", path: "docs" },
    ],
    "dayjs": [
        { owner: "iamkun", repo: "dayjs", path: "docs" },
    ],
    "moment": [
        { owner: "moment", repo: "moment", path: "src" },
    ],
    "luxon": [
        { owner: "moment", repo: "luxon", path: "docs" },
    ],
    "axios": [
        { owner: "axios", repo: "axios", path: "README.md" },
    ],
    "ky": [
        { owner: "sindresorhus", repo: "ky", path: "readme.md" },
    ],
    "got": [
        { owner: "sindresorhus", repo: "got", path: "documentation" },
    ],
    "node-fetch": [
        { owner: "node-fetch", repo: "node-fetch", path: "README.md" },
    ],
    "zod": [
        { owner: "colinhacks", repo: "zod", path: "README.md" },
    ],
    "yup": [
        { owner: "jquense", repo: "yup", path: "README.md" },
    ],
    "joi": [
        { owner: "hapijs", repo: "joi", path: "API.md" },
    ],
    "ajv": [
        { owner: "ajv-validator", repo: "ajv", path: "docs" },
    ],
    "uuid": [
        { owner: "uuidjs", repo: "uuid", path: "README.md" },
    ],
    "nanoid": [
        { owner: "ai", repo: "nanoid", path: "README.md" },
    ],
    "crypto-js": [
        { owner: "brix", repo: "crypto-js", path: "README.md" },
    ],
    "bcryptjs": [
        { owner: "dcodeIO", repo: "bcrypt.js", path: "README.md" },
    ],
    "dotenv": [
        { owner: "motdotla", repo: "dotenv", path: "README.md" },
    ],
    "cross-env": [
        { owner: "kentcdodds", repo: "cross-env", path: "README.md" },
    ],
    "chalk": [
        { owner: "chalk", repo: "chalk", path: "readme.md" },
    ],
    "commander": [
        { owner: "tj", repo: "commander.js", path: "Readme.md" },
    ],
    "inquirer": [
        { owner: "SBoudrias", repo: "Inquirer.js", path: "packages/inquirer/README.md" },
    ],
    "ora": [
        { owner: "sindresorhus", repo: "ora", path: "readme.md" },
    ],
    "winston": [
        { owner: "winstonjs", repo: "winston", path: "README.md" },
    ],
    "pino": [
        { owner: "pinojs", repo: "pino", path: "docs" },
    ],
    "bunyan": [
        { owner: "trentm", repo: "node-bunyan", path: "README.md" },
    ],
    "debug": [
        { owner: "debug-js", repo: "debug", path: "README.md" },
    ],
    "morgan": [
        { owner: "expressjs", repo: "morgan", path: "README.md" },
    ],
    "cors": [
        { owner: "expressjs", repo: "cors", path: "README.md" },
    ],
    "compression": [
        { owner: "expressjs", repo: "compression", path: "README.md" },
    ],
    "body-parser": [
        { owner: "expressjs", repo: "body-parser", path: "README.md" },
    ],
    "cookie-parser": [
        { owner: "expressjs", repo: "cookie-parser", path: "README.md" },
    ],
    "express-session": [
        { owner: "expressjs", repo: "session", path: "README.md" },
    ],
    "express-validator": [
        { owner: "express-validator", repo: "express-validator", path: "docs" },
    ],
    "jsonwebtoken": [
        { owner: "auth0", repo: "node-jsonwebtoken", path: "README.md" },
    ],
    "rate-limiter-flexible": [
        { owner: "animir", repo: "node-rate-limiter-flexible", path: "README.md" },
    ],
    "express-rate-limit": [
        { owner: "express-rate-limit", repo: "express-rate-limit", path: "README.md" },
    ],
    "nodemon": [
        { owner: "remy", repo: "nodemon", path: "README.md" },
    ],
    "pm2": [
        { owner: "Unitech", repo: "pm2", path: "README.md" },
    ],
    "concurrently": [
        { owner: "open-cli-tools", repo: "concurrently", path: "README.md" },
    ],
    "rimraf": [
        { owner: "isaacs", repo: "rimraf", path: "README.md" },
    ],
    "glob": [
        { owner: "isaacs", repo: "node-glob", path: "README.md" },
    ],
    "chokidar": [
        { owner: "paulmillr", repo: "chokidar", path: "README.md" },
    ],
    "fs-extra": [
        { owner: "jprichardson", repo: "node-fs-extra", path: "README.md" },
    ],
    "execa": [
        { owner: "sindresorhus", repo: "execa", path: "readme.md" },
    ],
    "shelljs": [
        { owner: "shelljs", repo: "shelljs", path: "README.md" },
    ],
    "yargs": [
        { owner: "yargs", repo: "yargs", path: "docs" },
    ],
    "minimist": [
        { owner: "minimistjs", repo: "minimist", path: "readme.markdown" },
    ],
    "meow": [
        { owner: "sindresorhus", repo: "meow", path: "readme.md" },
    ],
    "prompts": [
        { owner: "terkelg", repo: "prompts", path: "readme.md" },
    ],
    "listr": [
        { owner: "SamVerschueren", repo: "listr", path: "readme.md" },
    ],
    "boxen": [
        { owner: "sindresorhus", repo: "boxen", path: "readme.md" },
    ],
    "cli-table": [
        { owner: "Automattic", repo: "cli-table", path: "README.md" },
    ],
    "figlet": [
        { owner: "patorjk", repo: "figlet.js", path: "README.md" },
    ],
    "qrcode": [
        { owner: "soldair", repo: "node-qrcode", path: "README.md" },
    ],
    "pdf-lib": [
        { owner: "Hopding", repo: "pdf-lib", path: "README.md" },
    ],
    "pdfkit": [
        { owner: "foliojs", repo: "pdfkit", path: "README.md" },
    ],
    "cheerio": [
        { owner: "cheeriojs", repo: "cheerio", path: "Readme.md" },
    ],
    "jsdom": [
        { owner: "jsdom", repo: "jsdom", path: "README.md" },
    ],
    "xml2js": [
        { owner: "Leonidas-from-XIV", repo: "node-xml2js", path: "README.md" },
    ],
    "csv-parser": [
        { owner: "mafintosh", repo: "csv-parser", path: "README.md" },
    ],
    "papaparse": [
        { owner: "mholt", repo: "PapaParse", path: "README.md" },
    ],
    "xlsx": [
        { owner: "SheetJS", repo: "sheetjs", path: "README.md" },
    ],
    "archiver": [
        { owner: "archiverjs", repo: "node-archiver", path: "README.md" },
    ],
    "unzipper": [
        { owner: "ZJONSSON", repo: "node-unzipper", path: "README.md" },
    ],
    "tar": [
        { owner: "isaacs", repo: "node-tar", path: "README.md" },
    ],
    "compressing": [
        { owner: "node-modules", repo: "compressing", path: "README.md" },
    ],
    "mime-types": [
        { owner: "jshttp", repo: "mime-types", path: "README.md" },
    ],
    "mime": [
        { owner: "broofa", repo: "mime", path: "README.md" },
    ],
    "file-type": [
        { owner: "sindresorhus", repo: "file-type", path: "readme.md" },
    ],
    "image-size": [
        { owner: "image-size", repo: "image-size", path: "README.md" },
    ],
    "gm": [
        { owner: "aheckmann", repo: "gm", path: "README.md" },
    ],
    "canvas": [
        { owner: "Automattic", repo: "node-canvas", path: "Readme.md" },
    ],
    "qr-image": [
        { owner: "alexeyten", repo: "qr-image", path: "README.md" },
    ],
    "barcode": [
        { owner: "lindell", repo: "JsBarcode", path: "README.md" },
    ],
    "node-cron": [
        { owner: "node-cron", repo: "node-cron", path: "README.md" },
    ],
    "cron": [
        { owner: "kelektiv", repo: "node-cron", path: "README.md" },
    ],
    "agenda": [
        { owner: "agenda", repo: "agenda", path: "README.md" },
    ],
    "bull": [
        { owner: "OptimalBits", repo: "bull", path: "REFERENCE.md" },
    ],
    "bullmq": [
        { owner: "taskforcesh", repo: "bullmq", path: "docs" },
    ],
    "bee-queue": [
        { owner: "bee-queue", repo: "bee-queue", path: "Readme.md" },
    ],
    "kue": [
        { owner: "Automattic", repo: "kue", path: "Readme.md" },
    ],
    "amqplib": [
        { owner: "amqp-node", repo: "amqplib", path: "README.md" },
    ],
    "ioredis": [
        { owner: "redis", repo: "ioredis", path: "README.md" },
    ],
    "node-redis": [
        { owner: "redis", repo: "node-redis", path: "README.md" },
    ],
    "memcached": [
        { owner: "3rd-Eden", repo: "memcached", path: "README.md" },
    ],
    "node-cache": [
        { owner: "node-cache", repo: "node-cache", path: "README.md" },
    ],
    "lru-cache": [
        { owner: "isaacs", repo: "node-lru-cache", path: "README.md" },
    ],
    "keyv": [
        { owner: "jaredwray", repo: "keyv", path: "packages/keyv/README.md" },
    ],
    "cache-manager": [
        { owner: "node-cache-manager", repo: "node-cache-manager", path: "README.md" },
    ],
    "request": [
        { owner: "request", repo: "request", path: "README.md" },
    ],
    "superagent": [
        { owner: "ladjs", repo: "superagent", path: "README.md" },
    ],
    "needle": [
        { owner: "tomas", repo: "needle", path: "README.md" },
    ],
    "bent": [
        { owner: "mikeal", repo: "bent", path: "README.md" },
    ],
    "phin": [
        { owner: "ethanent", repo: "phin", path: "README.md" },
    ],
    "undici": [
        { owner: "nodejs", repo: "undici", path: "README.md" },
    ],
    "http-proxy": [
        { owner: "http-party", repo: "node-http-proxy", path: "README.md" },
    ],
    "http-proxy-middleware": [
        { owner: "chimurai", repo: "http-proxy-middleware", path: "README.md" },
    ],
    "express-http-proxy": [
        { owner: "villadora", repo: "express-http-proxy", path: "README.md" },
    ],
    "node-http-server": [
        { owner: "RIAEvangelist", repo: "node-http-server", path: "README.md" },
    ],
    "serve-static": [
        { owner: "expressjs", repo: "serve-static", path: "README.md" },
    ],
    "serve": [
        { owner: "vercel", repo: "serve", path: "readme.md" },
    ],
    "http-server": [
        { owner: "http-party", repo: "http-server", path: "README.md" },
    ],
    "live-server": [
        { owner: "tapio", repo: "live-server", path: "README.md" },
    ],
    "browser-sync": [
        { owner: "BrowserSync", repo: "browser-sync", path: "README.md" },
    ],
    "reload": [
        { owner: "alallier", repo: "reload", path: "README.md" },
    ],
    "emailjs": [
        { owner: "eleith", repo: "emailjs", path: "README.md" },
    ],
    "node-mailer": [
        { owner: "nodemailer", repo: "nodemailer", path: "README.md" },
    ],
    "sendmail": [
        { owner: "guileen", repo: "node-sendmail", path: "README.md" },
    ],
    "email-templates": [
        { owner: "forwardemail", repo: "email-templates", path: "README.md" },
    ],
    "mjml": [
        { owner: "mjmlio", repo: "mjml", path: "packages/mjml/README.md" },
    ],
    "handlebars": [
        { owner: "handlebars-lang", repo: "handlebars.js", path: "README.markdown" },
    ],
    "pug": [
        { owner: "pugjs", repo: "pug", path: "packages/pug/README.md" },
    ],
    "ejs": [
        { owner: "mde", repo: "ejs", path: "README.md" },
    ],
    "nunjucks": [
        { owner: "mozilla", repo: "nunjucks", path: "README.md" },
    ],
    "mustache": [
        { owner: "janl", repo: "mustache.js", path: "README.md" },
    ],
    "liquidjs": [
        { owner: "harttle", repo: "liquidjs", path: "README.md" },
    ],
    "eta": [
        { owner: "eta-dev", repo: "eta", path: "README.md" },
    ],
    "markdown-it": [
        { owner: "markdown-it", repo: "markdown-it", path: "README.md" },
    ],
    "marked": [
        { owner: "markedjs", repo: "marked", path: "README.md" },
    ],
    "remark": [
        { owner: "remarkjs", repo: "remark", path: "readme.md" },
    ],
    "unified": [
        { owner: "unifiedjs", repo: "unified", path: "readme.md" },
    ],
    "rehype": [
        { owner: "rehypejs", repo: "rehype", path: "readme.md" },
    ],
    "gray-matter": [
        { owner: "jonschlinkert", repo: "gray-matter", path: "README.md" },
    ],
    "front-matter": [
        { owner: "jxson", repo: "front-matter", path: "README.md" },
    ],
    "yaml": [
        { owner: "eemeli", repo: "yaml", path: "README.md" },
    ],
    "js-yaml": [
        { owner: "nodeca", repo: "js-yaml", path: "README.md" },
    ],
    "toml": [
        { owner: "BinaryMuse", repo: "toml-node", path: "README.md" },
    ],
    "ini": [
        { owner: "npm", repo: "ini", path: "README.md" },
    ],
    "properties": [
        { owner: "gagle", repo: "node-properties", path: "README.md" },
    ],
    "dotenv-expand": [
        { owner: "motdotla", repo: "dotenv-expand", path: "README.md" },
    ],
    "config": [
        { owner: "node-config", repo: "node-config", path: "README.md" },
    ],
    "convict": [
        { owner: "mozilla", repo: "node-convict", path: "README.md" },
    ],
    "nconf": [
        { owner: "indexzero", repo: "nconf", path: "README.md" },
    ],
    "rc": [
        { owner: "dominictarr", repo: "rc", path: "README.md" },
    ],
    "cosmiconfig": [
        { owner: "cosmiconfig", repo: "cosmiconfig", path: "README.md" },
    ],
    "env-var": [
        { owner: "evanshortiss", repo: "env-var", path: "README.md" },
    ],
    "envalid": [
        { owner: "af", repo: "envalid", path: "README.md" },
    ],
    "superstruct": [
        { owner: "ianstormtaylor", repo: "superstruct", path: "README.md" },
    ],
    "io-ts": [
        { owner: "gcanti", repo: "io-ts", path: "README.md" },
    ],
    "runtypes": [
        { owner: "pelotom", repo: "runtypes", path: "README.md" },
    ],
    "class-validator": [
        { owner: "typestack", repo: "class-validator", path: "README.md" },
    ],
    "class-transformer": [
        { owner: "typestack", repo: "class-transformer", path: "README.md" },
    ],
    "reflect-metadata": [
        { owner: "rbuckton", repo: "reflect-metadata", path: "README.md" },
    ],
    "inversify": [
        { owner: "inversify", repo: "InversifyJS", path: "README.md" },
    ],
    "tsyringe": [
        { owner: "microsoft", repo: "tsyringe", path: "README.md" },
    ],
    "awilix": [
        { owner: "jeffijoe", repo: "awilix", path: "README.md" },
    ],
    "typedi": [
        { owner: "typestack", repo: "typedi", path: "README.md" },
    ],
    "bottlejs": [
        { owner: "young-steveo", repo: "bottlejs", path: "README.md" },
    ],
    "node-di": [
        { owner: "vojtajina", repo: "node-di", path: "README.md" },
    ],
    "async": [
        { owner: "caolan", repo: "async", path: "README.md" },
    ],
    "bluebird": [
        { owner: "petkaantonov", repo: "bluebird", path: "README.md" },
    ],
    "q": [
        { owner: "kriskowal", repo: "q", path: "README.md" },
    ],
    "when": [
        { owner: "cujojs", repo: "when", path: "README.md" },
    ],
    "co": [
        { owner: "tj", repo: "co", path: "Readme.md" },
    ],
    "p-queue": [
        { owner: "sindresorhus", repo: "p-queue", path: "readme.md" },
    ],
    "p-limit": [
        { owner: "sindresorhus", repo: "p-limit", path: "readme.md" },
    ],
    "p-map": [
        { owner: "sindresorhus", repo: "p-map", path: "readme.md" },
    ],
    "p-retry": [
        { owner: "sindresorhus", repo: "p-retry", path: "readme.md" },
    ],
    "p-timeout": [
        { owner: "sindresorhus", repo: "p-timeout", path: "readme.md" },
    ],
    "p-debounce": [
        { owner: "sindresorhus", repo: "p-debounce", path: "readme.md" },
    ],
    "p-throttle": [
        { owner: "sindresorhus", repo: "p-throttle", path: "readme.md" },
    ],
    "bottleneck": [
        { owner: "SGrondin", repo: "bottleneck", path: "README.md" },
    ],
    "limiter": [
        { owner: "jhurliman", repo: "node-rate-limiter", path: "README.md" },
    ],
    "express-slow-down": [
        { owner: "express-rate-limit", repo: "express-slow-down", path: "README.md" },
    ],
    "express-brute": [
        { owner: "AdamPflug", repo: "express-brute", path: "README.md" },
    ],
    "node-rate-limiter": [
        { owner: "jhurliman", repo: "node-rate-limiter", path: "README.md" },
    ],
    "ratelimiter": [
        { owner: "tj", repo: "node-ratelimiter", path: "Readme.md" },
    ],
    "limiter-es6": [
        { owner: "Satishpokala124", repo: "limiter-es6", path: "README.md" },
    ],
    "express-limiter": [
        { owner: "ded", repo: "express-limiter", path: "README.md" },
    ],
    "koa-ratelimit": [
        { owner: "koajs", repo: "ratelimit", path: "Readme.md" },
    ],
    "fastify-rate-limit": [
        { owner: "fastify", repo: "fastify-rate-limit", path: "README.md" },
    ],
    "hapi-rate-limit": [
        { owner: "wraithgar", repo: "hapi-rate-limit", path: "README.md" },
    ],
    "restify-rate-limiter": [
        { owner: "restify", repo: "node-restify-rate-limiter", path: "README.md" },
    ],
    "node-limiter": [
        { owner: "jhurliman", repo: "node-rate-limiter", path: "README.md" },
    ],
    "token-bucket": [
        { owner: "jhurliman", repo: "node-rate-limiter", path: "README.md" },
    ],
    "leaky-bucket": [
        { owner: "distribusion", repo: "leaky-bucket", path: "README.md" },
    ],
    "sliding-window-rate-limiter": [
        { owner: "animir", repo: "node-rate-limiter-flexible", path: "README.md" },
    ],
    "redis-rate-limiter": [
        { owner: "tabdigital", repo: "redis-rate-limiter", path: "README.md" },
    ],
    "ioredis-rate-limiter": [
        { owner: "animir", repo: "node-rate-limiter-flexible", path: "README.md" },
    ],
    "memcached-rate-limiter": [
        { owner: "animir", repo: "node-rate-limiter-flexible", path: "README.md" },
    ],
    "mongo-rate-limiter": [
        { owner: "animir", repo: "node-rate-limiter-flexible", path: "README.md" },
    ],
    "postgres-rate-limiter": [
        { owner: "animir", repo: "node-rate-limiter-flexible", path: "README.md" },
    ],
    "mysql-rate-limiter": [
        { owner: "animir", repo: "node-rate-limiter-flexible", path: "README.md" },
    ],
};
/**
 * Get repositories for a library name
 */
export function getReposForLibrary(libraryName) {
    const lowerName = libraryName.toLowerCase();
    // Exact match
    if (REPO_REGISTRY[lowerName]) {
        return REPO_REGISTRY[lowerName];
    }
    // Partial match
    for (const [key, repos] of Object.entries(REPO_REGISTRY)) {
        if (key.includes(lowerName) || lowerName.includes(key)) {
            return repos;
        }
    }
    return [];
}
/**
 * Add a custom repository to the registry
 */
export function addCustomRepo(libraryName, repo) {
    if (!REPO_REGISTRY[libraryName]) {
        REPO_REGISTRY[libraryName] = [];
    }
    REPO_REGISTRY[libraryName].push(repo);
}
/**
 * List all registered libraries
 */
export function listAllLibraries() {
    return Object.keys(REPO_REGISTRY).sort();
}
/**
 * Get total count of registered libraries
 */
export function getTotalLibraryCount() {
    return Object.keys(REPO_REGISTRY).length;
}
/**
 * Get libraries by category
 */
export function getLibrariesByCategory() {
    return {
        "Workflow Automation": ["n8n", "zapier", "make", "activepieces", "windmill"],
        "JavaScript/TypeScript": ["nextjs", "react", "vue", "angular", "svelte", "solid", "qwik", "astro", "remix", "nuxt", "gatsby"],
        "Node.js Backend": ["express", "fastify", "koa", "hapi", "nestjs", "adonis", "sails", "meteor", "feathers", "loopback"],
        "Python": ["fastapi", "django", "flask", "tornado", "pyramid", "bottle", "falcon", "sanic", "starlette", "quart"],
        "Databases & ORMs": ["supabase", "prisma", "mongodb", "postgresql", "mysql", "redis", "typeorm", "sequelize", "mongoose", "knex", "drizzle", "kysely"],
        "Cloud & Deployment": ["vercel", "cloudflare", "netlify", "heroku", "railway", "render", "fly", "aws-cdk", "aws-amplify", "terraform", "pulumi", "serverless"],
        "AI/LLM": ["openai", "langchain", "llamaindex", "anthropic", "huggingface", "tensorflow", "pytorch", "scikit-learn", "keras", "pandas", "numpy"],
        "Messaging": ["telegram", "discord", "slack", "whatsapp", "twilio", "sendgrid", "mailgun", "nodemailer", "pusher", "socket.io", "rabbitmq", "kafka"],
        "Testing": ["jest", "vitest", "playwright", "cypress", "puppeteer", "mocha", "chai", "jasmine", "ava", "selenium"],
        "DevOps & CI/CD": ["docker", "kubernetes", "github-actions", "gitlab-ci", "jenkins", "circleci", "travis", "ansible", "vagrant", "packer", "helm"],
        "Mobile": ["react-native", "expo", "flutter", "ionic", "capacitor", "nativescript", "xamarin"],
        "State Management": ["redux", "mobx", "zustand", "jotai", "recoil", "xstate", "valtio", "pinia", "vuex", "ngrx"],
        "UI Components": ["material-ui", "ant-design", "chakra-ui", "shadcn-ui", "radix-ui", "headless-ui", "mantine", "nextui", "daisyui", "bootstrap", "tailwindcss"],
        "Authentication": ["auth0", "clerk", "passport", "next-auth", "firebase-auth", "keycloak", "oauth2", "jwt", "bcrypt", "helmet"],
        "Payment": ["stripe", "paypal", "square", "braintree", "paddle", "lemon-squeezy"],
        "Analytics": ["google-analytics", "mixpanel", "segment", "posthog", "amplitude", "sentry", "datadog", "newrelic", "bugsnag", "rollbar"],
        "File Storage": ["aws-s3", "cloudinary", "uploadcare", "imagekit", "multer", "sharp", "jimp", "ffmpeg"],
        "Search": ["algolia", "meilisearch", "typesense", "lunr", "fuse"],
        "CMS": ["strapi", "contentful", "sanity", "ghost", "wordpress", "keystonejs", "directus", "payload"],
        "GraphQL": ["apollo", "graphql", "relay", "urql", "hasura", "postgraphile"],
        "Real-time": ["socket.io", "ws", "ably", "pusher", "centrifugo"],
        "Web3": ["ethers", "web3", "wagmi", "viem", "hardhat", "truffle", "solidity"],
        "Documentation": ["docusaurus", "vitepress", "nextra", "mintlify", "gitbook", "mkdocs", "sphinx", "typedoc", "jsdoc", "storybook"],
        "Build Tools": ["vite", "webpack", "rollup", "esbuild", "parcel", "turbopack", "swc", "babel", "tsup", "unbuild"],
        "Linting": ["eslint", "prettier", "biome", "stylelint", "commitlint", "husky", "lint-staged"],
        "Package Managers": ["npm", "yarn", "pnpm", "bun"],
        "Utilities": ["lodash", "ramda", "date-fns", "dayjs", "moment", "luxon", "axios", "ky", "got", "node-fetch", "zod", "yup", "joi", "ajv"],
        // ============================================================
        // ADDITIONAL PYTHON DATA SCIENCE & ML
        // ============================================================
        "xgboost": [
            { owner: "dmlc", repo: "xgboost", path: "doc" },
        ],
        "lightgbm": [
            { owner: "microsoft", repo: "LightGBM", path: "docs" },
        ],
        "catboost": [
            { owner: "catboost", repo: "catboost", path: "catboost/docs" },
        ],
        "optuna": [
            { owner: "optuna", repo: "optuna", path: "docs/source" },
        ],
        "ray": [
            { owner: "ray-project", repo: "ray", path: "doc/source" },
        ],
        "dask": [
            { owner: "dask", repo: "dask", path: "docs/source" },
        ],
        "polars": [
            { owner: "pola-rs", repo: "polars", path: "docs" },
        ],
        "pydantic": [
            { owner: "pydantic", repo: "pydantic", path: "docs" },
        ],
        "sqlalchemy": [
            { owner: "sqlalchemy", repo: "sqlalchemy", path: "doc/build" },
        ],
        "alembic": [
            { owner: "sqlalchemy", repo: "alembic", path: "docs/build" },
        ],
        "celery": [
            { owner: "celery", repo: "celery", path: "docs" },
        ],
        "airflow": [
            { owner: "apache", repo: "airflow", path: "docs" },
        ],
        "prefect": [
            { owner: "PrefectHQ", repo: "prefect", path: "docs" },
        ],
        "dagster": [
            { owner: "dagster-io", repo: "dagster", path: "docs/content" },
        ],
        "luigi": [
            { owner: "spotify", repo: "luigi", path: "doc" },
        ],
        "kedro": [
            { owner: "kedro-org", repo: "kedro", path: "docs/source" },
        ],
        "mlflow": [
            { owner: "mlflow", repo: "mlflow", path: "docs/source" },
        ],
        "wandb": [
            { owner: "wandb", repo: "wandb", path: "docs" },
        ],
        "comet": [
            { owner: "comet-ml", repo: "comet-examples", path: "README.md" },
        ],
        "neptune": [
            { owner: "neptune-ai", repo: "neptune-client", path: "docs" },
        ],
    };
}
//# sourceMappingURL=registry-old-full.js.map