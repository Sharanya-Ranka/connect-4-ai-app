import logo from "./logo.svg";
import "./App.css";

import { Analytics } from "@vercel/analytics/react";

import { BrowserRouter, Route, Routes, Link } from "react-router-dom";
import Game from "./components/Game/Game.jsx";
import BlogMain from "./components/Blog/BlogMain.jsx";
import Navbar from "./components/Navbar/Navbar.jsx";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <div>
          <Navbar />
          <Routes>
            <Route path="/blog" element={<BlogMain />} />
            <Route path="/" element={<Game />} />
          </Routes>
        </div>
      </BrowserRouter>
      <Analytics />
    </div>
  );
}

export default App;
