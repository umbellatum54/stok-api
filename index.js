const express = require("express");
const app = express();

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Stok API çalışıyor 🚀");
});

app.get("/test", (req, res) => {
  res.json({ status: "ok" });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log("Server çalışıyor: " + PORT);
});
