x=($(ls *.py))
for i in "${x[@]}"
do
	modulegraph $i | dot -T png -o $i.png
done
