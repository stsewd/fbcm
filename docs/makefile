FILES = requirements.md \
		metadata.yaml

OUTPUT = build

FLAGS = -s \
		-f markdown \

FLAGS_PDF =

all: html pdf

html:
	pandoc -o $(OUTPUT)/requirements.html $(FLAGS) $(FILES)

pdf:
	pandoc -o $(OUTPUT)/requirements.pdf $(FLAGS) $(FLAGS_PDF) $(FILES)

clean:
	rm build/*

