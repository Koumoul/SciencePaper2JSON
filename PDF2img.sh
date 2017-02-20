#transforme tout les pdf d"un dosser en image et suprime les PDF

cd $1
shopt -s nullglob
for pdf in *{pdf,PDF} ; do
    sips -s format jpeg "$pdf" --out "${pdf%%.*}.jpeg" &> /dev/null
    rm "$pdf"
done
