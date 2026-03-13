/**
 * Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "DIOTEC 360 IA Studio - Correct-by-Construction Software",
  description: "Interactive playground for DIOTEC 360 IA. Write code that is mathematically proved to be correct.",
  keywords: ["diotec 360", "diotec 360 ia", "formal verification", "correct by construction", "z3 solver"],
  authors: [{ name: "DIOTEC 360" }],
  openGraph: {
    title: "DIOTEC 360 IA Studio",
    description: "Write software that is mathematically proved to be correct",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
