import { Sparkles, Zap, Brain, Code2, Rocket } from 'lucide-react'

export default function HomePage() {
    return (
        <div className="max-w-7xl mx-auto">
            {/* Hero Section */}
            <div className="text-center py-20 animate-fade-in">
                <div className="inline-flex items-center gap-2 px-4 py-2 glass-card mb-8">
                    <Sparkles className="text-dive-primary animate-pulse" size={20} />
                    <span className="text-sm">Dive AI V29.4 - Self-Evolving System</span>
                </div>

                <h1 className="text-7xl font-bold mb-6 bg-gradient-to-r from-dive-primary via-dive-secondary to-dive-accent bg-clip-text text-transparent animate-slide-up">
                    AI-Powered Coding
                    <br />
                    <span className="text-6xl">Redefined</span>
                </h1>

                <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-12">
                    Experience the future of programming with 50+ intelligent algorithms,
                    self-evolving capabilities, and seamless multi-channel integration.
                </p>

                <div className="flex gap-4 justify-center">
                    <button className="glow-button group">
                        Get Started
                        <Rocket className="inline-block ml-2 group-hover:translate-x-1 transition-transform" size={20} />
                    </button>
                    <button className="glass-card px-6 py-3 rounded-lg hover:bg-dive-surface-light transition-all">
                        View Documentation
                    </button>
                </div>
            </div>

            {/* Features Grid */}
            <div className="grid md:grid-cols-3 gap-6 mt-20">
                <FeatureCard
                    icon={<Brain className="text-dive-primary" size={32} />}
                    title="AI Algorithm Selection"
                    description="Intelligently chooses the best algorithm for each task using advanced AI reasoning"
                />
                <FeatureCard
                    icon={<Zap className="text-dive-accent" size={32} />}
                    title="Self-Evolving System"
                    description="Automatically generates and optimizes algorithms based on execution patterns"
                />
                <FeatureCard
                    icon={<Code2 className="text-dive-secondary" size={32} />}
                    title="Code Generation"
                    description="Transform natural language into production-ready code across multiple languages"
                />
            </div>

            {/* Stats */}
            <div className="grid md:grid-cols-4 gap-6 mt-20">
                <StatCard number="50+" label="Algorithms" />
                <StatCard number="128" label="Agents" />
                <StatCard number="636" label="Skills" />
                <StatCard number="99.9%" label="Uptime" />
            </div>
        </div>
    )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
    return (
        <div className="glass-card p-8 hover:scale-105 transition-all duration-300 group cursor-pointer">
            <div className="mb-4 group-hover:scale-110 transition-transform">
                {icon}
            </div>
            <h3 className="text-xl font-semibold mb-3 text-white">{title}</h3>
            <p className="text-gray-400">{description}</p>
        </div>
    )
}

function StatCard({ number, label }: { number: string; label: string }) {
    return (
        <div className="glass-card p-6 text-center">
            <div className="text-4xl font-bold bg-gradient-to-r from-dive-primary to-dive-secondary bg-clip-text text-transparent mb-2">
                {number}
            </div>
            <div className="text-gray-400 text-sm uppercase tracking-wide">{label}</div>
        </div>
    )
}
