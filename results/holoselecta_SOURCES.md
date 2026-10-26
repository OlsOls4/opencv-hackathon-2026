# HoloSelecta — sources and licence note (first 20 images only)

- Dataset: HoloSelecta Dataset (10'035 annotated images of packaged
  products with GTIN & nutrients), Mendeley Data
- URL: https://data.mendeley.com/datasets/gz39ggf35n/1
- DOI: 10.17632/gz39ggf35n.1, published 24 August 2020, version 1
- Contributors: Klaus Fuchs, Tobias Grundmann, Mirella Haldimann, Elgar Fleisch
- Cite: Fuchs K, Haldimann M, Grundmann T, Fleisch E. Supporting food
  choices in the Internet of People. Futur Gener Comput Syst 2020;113:343–62.
  https://doi.org/10.1016/j.future.2020.07.014
- Files listed by the Mendeley files API (no login, no payment required):
  - HoloSelecta-FinalDataset-20200127T164214Z-001.zip, 2,122,992,435 bytes
    (~2.0 GiB), SHA256 in files API:
    4492e5f544a035cf4884626187ebf39ab5e703f71a3ff05733b6c11baf926afb
  - Datainbrief_HoloSelecta_v3mendeley.pdf, 243,939 bytes
  - product_meta_data.py, 27,562 bytes
- What was actually downloaded: the full zip was NOT completed. About
  1.1 GB was downloaded, then the download was stopped, and the first
  20 images + their PascalVOC XMLs were extracted by streaming unzip
  from the partial file. Extracted set: 20 JPGs (~100 MB total) + 82 XMLs
  encountered before the 20th image, in ~/workspace/holoselecta/extract20/
  (outside the ShelfScan repo).
- Licence status — read carefully: the Mendeley dataset page text fetched
  showed NO licence line. However, the DOI response headers for
  10.17632/gz39ggf35n.1 carry rel="licence"
  http://creativecommons.org/licenses/by/4.0 (CC BY 4.0). That is the
  basis for treating the dataset as CC BY 4.0, consistent with the paper
  being CC BY 4.0, but the dataset page itself did not display a licence
  line in the fetch — so do NOT re-licence it as MIT, and do NOT bundle
  the dataset images in the GitHub repo. Images stay local only.
  Annotated copies in results/holoselecta_annotated/ are local
  evaluation artefacts, not for GitHub push.
- Ground truth used: PascalVOC XML <object> count per image; GT names are
  product + GTIN strings, 17–40 distinct products per image in this set.
- Ground truth file: eval/holoselecta_ground_truth.csv, columns
  image,class,manual_count, with class intentionally empty (total-count
  semantics: YOLO count vs total GT boxes, no labelling claim).
  The pre-existing eval/ground_truth.csv (header only) was left intact.
- Results: results/holoselecta_eval_results.json/.csv,
  results/holoselecta_failures.md, this file. Model: YOLO26n ONNX,
  OpenCV 5.0.0, confidence 0.35, via app/inference.py Detector.
