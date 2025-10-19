const fs = require("fs");
const csv = require("csv-parser");

const students = [];
fs.createReadStream("students.csv")
  .pipe(csv())
  .on("data", (row) => students.push(row))
  .on("end", () => {
    main();
  });



//not mine original formula/function, got from google 
function cosineSimilarity(a, b) {
  const dot = a.reduce((sum, x, i) => sum + x * b[i], 0);
  const normA = Math.sqrt(a.reduce((sum, x) => sum + x * x, 0));
  const normB = Math.sqrt(b.reduce((sum, x) => sum + x * x, 0));
  return normA && normB ? dot / (normA * normB) : 0;
}



function main() {
  const majors = [...new Set(students.map(s => s.major))].sort();

  console.log("\n")
  console.log("majors: ")
  console.log(majors);
  console.log("\n")




  const interests = [...new Set(
    students.flatMap(s => s.interests.split(";").map(i => i.trim()))
  )].sort();

  console.log("\n")
  console.log("interests: ")
  console.log(interests);
  console.log("\n")



  const studyTimeMap = { morning: 0, evening: 1 };

  function rowToVector(student) {
    const vec = [];

    for (const m of majors) vec.push(student.major === m ? 1 : 0);

    vec.push(Number(student.year) / 4.0); //divide by 4 because max uni is 4 years (so its between 0 to 1)

    const ints = student.interests.split(";").map(i => i.trim());


    for(let i=0; i<interests.length; i++) {
      vec.push(ints.includes(interests[i]) ? 1 : 0);
    }

    vec.push(studyTimeMap[student.study_time] ?? 0);

    return vec;
  }

  console.log("\n")
  console.log("students: ")
  console.log(students.map(s => rowToVector(s)));
  console.log("\n")

  const vectors = Object.fromEntries(
    students.map(student => [student.id, rowToVector(student)])
  );


  // run the cosine similarity
  const IDs = students.map(student => student.id);
  const n = IDs.length;
  const scores = Array.from({ length: n }, () => Array(n).fill(0));

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      scores[i][j] = cosineSimilarity(vectors[IDs[i]], vectors[IDs[j]]);
    }
  }

  console.log("\n")
  console.log("scores: ")
  console.log(scores);
  console.log("\n")

  //check if its a match
  const isAMatch = 0.7;
  const matchScores = scores.map(row => row.map(val => val >= isAMatch));


  //check reflexive, symmetric, transitive
  const reflexive = matchScores.every((row, i) => row[i]);

  const symmetric = matchScores.every((row, i) =>
    row.every((v, j) => v === matchScores[j][i])
  );

  let transitive = true;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (matchScores[i][j]) {
        for (let k = 0; k < n; k++) {
          if (matchScores[j][k] && !matchScores[i][k]) transitive = false;
        }
      }
    }
  }


  //console log final input
  console.log("IDs:", IDs);
  console.log("Score matrix:");
  console.table(scores.map(row => row.map(v => Number(v.toFixed(3)))));


  console.log("\n");
  console.log("Score 0.7 +:");
  console.table(matchScores);

  console.log("\n");
  console.log("Reflexive?", reflexive);
  console.log("Symmetric?", symmetric);
  console.log("Transitive?", transitive);

  // show top matches
  for (let i = 0; i < n; i++) {
    const pairs = IDs.map((id, j) => ({ id, score: scores[i][j] }))
      .filter(p => p.id !== IDs[i]) //remove itself from this try
      .sort((a, b) => b.score - a.score) //sort highest to lowest
      .slice(0, 3); //show only top 3


    console.log(`Top matches for ${IDs[i]}:`, pairs);
  }
}
