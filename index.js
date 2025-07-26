const express = require("express");
const app = express()
app.use(express.json());
app.post("/", (req, res ) => {
    console.log(req.body);
    return res.json({message: req.body})

});
app.listen(3000, () => {
    console.log("Webhook started")
})

