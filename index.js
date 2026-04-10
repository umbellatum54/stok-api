const express = require("express");
const app = express();

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Stok API çalışıyor 🚀");
});

app.get("/test", (req, res) => {
  res.json({ status: "ok" });
});

// 🔥 BURASI ÇOK KRİTİK
const PORT = process.env.PORT;

app.listen(PORT, "0.0.0.0", () => {
  console.log("Server çalışıyor: " + PORT);
});
