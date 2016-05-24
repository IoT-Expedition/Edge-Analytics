for N in {1..8}; do ./util/align-dlib.py ./data/mydataset/raw align outerEyesAndNose ./data/mydataset/aligned --size 96& done
luajit ./batch-represent/main.lua -data ./data/mydataset/aligned -outDir ./data/mydataset/reps -model ./models/openface/nn4.small2.v1.t7
./demos/classifier.py train  ./data/mydataset/reps