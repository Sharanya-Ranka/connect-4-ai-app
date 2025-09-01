// src/components/Navbar.js
import React, { useState } from "react";
import { Link } from "react-router-dom";
import "../../styles/Navbar/Navbar.css"; // Import CSS
import GameInfo from "./GameInfo";
import BlogInfo from "./BlogInfo";

function Navbar() {
  const [showGameDetails, setShowGameDetails] = useState(false);
  const [showBlogDetails, setShowBlogDetails] = useState(false);

  return (
    <nav className="navbar">
      <ul className="nav-list">
        <li
          className="nav-item"
          onMouseEnter={() => {
            setShowGameDetails(true);
            setShowBlogDetails(false);
          }}
          onMouseLeave={() => setShowGameDetails(false)}
        >
          <Link to="/">Game</Link>
          {showGameDetails && (
            <div className="details-overlay">
              <GameInfo />
              {/* Add game details component or content here */}
            </div>
          )}
        </li>
        <li
          className="nav-item"
          onMouseEnter={() => {
            setShowBlogDetails(true);
            setShowGameDetails(false);
          }}
          onMouseLeave={() => setShowBlogDetails(false)}
        >
          <Link to="/blog">Blog</Link>
          {showBlogDetails && (
            <div className="details-overlay">
              <BlogInfo />
              {/* Add blog details component or content here */}
            </div>
          )}
        </li>
      </ul>
    </nav>
  );
}

export default Navbar;
