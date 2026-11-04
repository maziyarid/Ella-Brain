import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const gate = "http://127.0.0.1:8765";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { host: "127.0.0.1", proxy: { "/v1": gate } },
  preview: { host: "127.0.0.1", proxy: { "/v1": gate } },
});
