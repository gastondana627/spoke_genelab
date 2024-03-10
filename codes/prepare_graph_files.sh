
echo 'Starting get_assay_node.ipynb ...'
jupyter-nbconvert --to notebook --inplace --ExecutePreprocessor.timeout=None --execute get_assay_node.ipynb
if [ $? -eq 0 ]; then
    echo 'get_assay_node.ipynb completed successfully!'
else
    echo 'Error: get_assay_node.ipynb execution failed.'
    exit 1
fi

echo 'Starting get_mgene_node.ipynb ...'
jupyter-nbconvert --to notebook --inplace --ExecutePreprocessor.timeout=None --execute get_mgene_node.ipynb
if [ $? -eq 0 ]; then
    echo 'get_mgene_node.ipynb completed successfully!'
else
    echo 'Error: get_mgene_node.ipynb execution failed.'
    exit 1
fi

