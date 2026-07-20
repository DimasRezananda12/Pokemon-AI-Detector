export default function Footer() {
  return (
    <footer className="bg-dark-surface border-t border-dark-border mt-auto py-8 text-sm">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="font-semibold text-neutral-400">
          © 2026 PokeAuthAI. Professional Verification Systems.
        </div>
        <div className="flex gap-6 text-neutral-400">
          <a href="#" className="hover:text-white transition-colors no-underline text-xs">Privacy Policy</a>
          <a href="#" className="hover:text-white transition-colors no-underline text-xs">Terms of Service</a>
          <a href="#" className="hover:text-white transition-colors no-underline text-xs">Security</a>
          <a href="#" className="hover:text-white transition-colors no-underline text-xs">Contact</a>
        </div>
      </div>
    </footer>
  );
}
