import logo from "./logo.svg";
import "./App.css";
import MainComponent from "./components/MainComponent";
import { Analytics } from "@vercel/analytics/react";
import GameInfo from "./components/GameInfo/GameInfo";

function App() {
  return (
    <div className="App">
      <GameInfo />
      <MainComponent />
      <Analytics />
    </div>
  );
}

export default App;
