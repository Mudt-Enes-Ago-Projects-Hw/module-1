import pandas as pd
import numpy as np

# Read CSV
students = pd.read_csv("students.csv").to_dict(orient="records")

# Cosine similarity function
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0

# Main logic
def main():
    # Get unique majors
    majors = sorted({s["major"] for s in students})
    print("\nmajors:\n", majors)

    # Get unique interests
    all_interests = sorted({i.strip() for s in students for i in s["interests"].split(";")})
    print("\ninterests:\n", all_interests)

    study_time_map = {"morning": 0, "evening": 1}

    def row_to_vector(student):
        vec = []
        # Major one-hot
        vec.extend([1 if student["major"] == m else 0 for m in majors])
        # Year normalized (assuming max 4)
        vec.append(int(student["year"]) / 4.0)
        # Interests one-hot
        student_interests = [i.strip() for i in student["interests"].split(";")]
        vec.extend([1 if i in student_interests else 0 for i in all_interests])
        # Study time
        vec.append(study_time_map.get(student.get("study_time", ""), 0))
        return vec

    print("\nstudents vectors:\n", [row_to_vector(s) for s in students])

    vectors = {s["id"]: row_to_vector(s) for s in students}

    # Cosine similarity matrix
    IDs = [s["id"] for s in students]
    n = len(IDs)
    scores = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            scores[i, j] = cosine_similarity(vectors[IDs[i]], vectors[IDs[j]])

    print("\nscores:\n", scores)

    # Threshold for match
    is_a_match = 0.7
    match_scores = scores >= is_a_match

    # Reflexive
    reflexive = all(match_scores[i, i] for i in range(n))
    # Symmetric
    symmetric = np.all(match_scores == match_scores.T)
    # Transitive
    transitive = True
    for i in range(n):
        for j in range(n):
            if match_scores[i, j]:
                for k in range(n):
                    if match_scores[j, k] and not match_scores[i, k]:
                        transitive = False

    print("\nIDs:", IDs)
    print("\nScore matrix (rounded 3 decimals):\n", np.round(scores, 3))
    print("\nScore 0.7+ matrix:\n", match_scores)
    print("\nReflexive?", reflexive)
    print("Symmetric?", symmetric)
    print("Transitive?", transitive)

    # Top matches for each student
    for i in range(n):
        pairs = sorted(
            [{"id": IDs[j], "score": scores[i, j]} for j in range(n) if j != i],
            key=lambda x: -x["score"]
        )[:3]
        print(f"Top matches for {IDs[i]}:", pairs)

if __name__ == "__main__":
    main()
